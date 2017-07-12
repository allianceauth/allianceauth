from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import User
from notifications import notify
from celery import task
from authentication.models import AuthServicesInfo
from eveonline.managers import EveManager
from eveonline.models import EveApiKeyPair
from services.managers.eve_api_manager import EveApiManager
from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo
from eveonline.providers import eve_adapter_factory, ObjectNotFound
from authentication.tasks import set_state
import logging
import evelink

from alliance_auth.celeryapp import app

logger = logging.getLogger(__name__)


@app.task
def refresh_api(api):
    logger.debug('Running update on api key %s' % api.api_id)
    still_valid = True
    try:
        EveApiManager.validate_api(api.api_id, api.api_key, api.user)
        # Update characters
        characters = EveManager.get_characters_from_api(api)
        for c in characters:
            try:
                EveManager.update_character_obj(c)
            except EveCharacter.DoesNotExist:
                logger.debug("API key %s has a new character on the account: %s" % (api.api_id, c))
                EveManager.create_character_obj(c, api.user, api.api_id)
        current_chars = EveCharacter.objects.filter(api_id=api.api_id)
        for c in current_chars:
            if not int(c.character_id) in [c.id for c in characters]:
                logger.info("Character %s no longer found on API ID %s" % (c, api.api_id))
                c.delete()
    except evelink.api.APIError as e:
        logger.warning('Received unexpected APIError (%s) while updating API %s' % (e.code, api.api_id))
    except EveApiManager.ApiInvalidError:
        logger.debug("API key %s is no longer valid; it and its characters will be deleted." % api.api_id)
        notify(api.user, "API Failed Validation", message="Your API key ID %s is no longer valid." % api.api_id,
               level="danger")
        still_valid = False
    except EveApiManager.ApiAccountValidationError:
        logger.info(
            "Determined api key %s for user %s no longer meets account access requirements." % (api.api_id, api.user))
        notify(api.user, "API Failed Validation",
               message="Your API key ID %s is no longer account-wide as required." % api.api_id, level="danger")
        still_valid = False
    except EveApiManager.ApiMaskValidationError as e:
        logger.info("Determined api key %s for user %s no longer meets minimum access mask as required." % (
            api.api_id, api.user))
        notify(api.user, "API Failed Validation",
               message="Your API key ID %s no longer meets access mask requirements. Required: %s Got: %s" % (
                   api.api_id, e.required_mask, e.api_mask), level="danger")
        still_valid = False
    except EveApiManager.ApiServerUnreachableError as e:
        logger.warn("Error updating API %s\n%s" % (api.api_id, str(e)))
    finally:
        if not still_valid:
            EveManager.delete_characters_by_api_id(api.api_id, api.user.id)
            EveManager.delete_api_key_pair(api.api_id, api.user.id)
            notify(api.user, "API Key Deleted",
                   message="Your API key ID %s is invalid. It and its associated characters have been deleted." % api.api_id,
                   level="danger")


@app.task
def refresh_user_apis(pk):
    user = User.objects.get(pk=pk)
    logger.debug('Refreshing all APIs belonging to user %s' % user)
    apis = EveApiKeyPair.objects.filter(user=user)
    for x in apis:
        refresh_api.apply(args=(x,))
    # Check our main character
    auth = AuthServicesInfo.objects.get(user=user)
    if auth.main_char_id:
        if EveCharacter.objects.filter(character_id=auth.main_char_id).exists() is False:
            logger.info(
                "User %s main character id %s missing model. Clearning main character." % (user, auth.main_char_id))
            auth.main_char_id = ''
            auth.save()
            notify(user, "Main Character Reset",
                   message="Your specified main character no longer has a model.\nThis could be the result of "
                           "an invalid API.\nYour main character ID has been reset.",
                   level="warn")
    set_state(user)


@app.task
def run_api_refresh():
    if not EveApiManager.check_if_api_server_online():
        logger.warn("Aborted scheduled API key refresh: API server unreachable")
        return

    for u in User.objects.all():
        refresh_user_apis.delay(u.pk)


@app.task
def update_corp(id, is_blue=None):
    EveManager.update_corporation(id, is_blue=is_blue)


@app.task
def update_alliance(id, is_blue=None):
    EveManager.update_alliance(id, is_blue=is_blue)
    EveManager.populate_alliance(id)


@app.task
def run_corp_update():
    if not EveApiManager.check_if_api_server_online():
        logger.warn("Aborted updating corp and alliance models: API server unreachable")
        return

    # generate member corps
    for corp_id in settings.STR_CORP_IDS + settings.STR_BLUE_CORP_IDS:
        is_blue = True if corp_id in settings.STR_BLUE_CORP_IDS else False
        try:
            if EveCorporationInfo.objects.filter(corporation_id=corp_id).exists():
                update_corp.apply(args=(corp_id,), kwargs={'is_blue': is_blue})
            else:
                EveManager.create_corporation(corp_id, is_blue=is_blue)
        except ObjectNotFound:
            logger.warn('Bad corp ID in settings: %s' % corp_id)

    # generate member alliances
    for alliance_id in settings.STR_ALLIANCE_IDS + settings.STR_BLUE_ALLIANCE_IDS:
        is_blue = True if alliance_id in settings.STR_BLUE_ALLIANCE_IDS else False
        try:
            if EveAllianceInfo.objects.filter(alliance_id=alliance_id).exists():
                logger.debug("Updating existing owner alliance model with id %s" % alliance_id)
                update_alliance(alliance_id, is_blue=is_blue)
            else:
                EveManager.create_alliance(alliance_id, is_blue=is_blue)
                EveManager.populate_alliance(alliance_id)
        except ObjectNotFound:
            logger.warn('Bad alliance ID in settings: %s' % alliance_id)

    # update existing corp models
    for corp in EveCorporationInfo.objects.exclude(
            corporation_id__in=settings.STR_CORP_IDS + settings.STR_BLUE_CORP_IDS):
        update_corp.delay(corp.corporation_id)

    # update existing alliance models
    for alliance in EveAllianceInfo.objects.exclude(
            alliance_id__in=settings.STR_ALLIANCE_IDS + settings.STR_BLUE_ALLIANCE_IDS):
        update_alliance.delay(alliance.alliance_id)

    try:
        # create standings
        standings = EveApiManager.get_corp_standings()
        if standings:
            standings = standings[settings.STANDING_LEVEL]
            for standing in standings:
                if float(standings[standing]['standing']) >= settings.BLUE_STANDING:
                    logger.debug("Standing %s meets threshold" % standing)
                    if EveApiManager.check_if_id_is_alliance(standing):
                        logger.debug("Standing %s is an alliance" % standing)
                        if EveAllianceInfo.objects.filter(alliance_id=standing).exists():
                            alliance = EveAllianceInfo.objects.get(alliance_id=standing)
                            if alliance.is_blue is not True:
                                logger.info("Updating alliance %s as blue" % alliance)
                                alliance.is_blue = True
                                alliance.save()
                        else:
                            EveManager.create_alliance(standing, is_blue=True)
                    elif EveApiManager.check_if_id_is_corp(standing):
                        logger.debug("Standing %s is a corp" % standing)
                        if EveCorporationInfo.objects.filter(corporation_id=standing).exists():
                            corp = EveCorporationInfo.objects.get(corporation_id=standing)
                            if corp.is_blue is not True:
                                logger.info("Updating corp %s as blue" % corp)
                                corp.is_blue = True
                                corp.save()
                        else:
                            logger.info("Creating model for blue corp with id %s" % standing)
                            EveManager.create_corporation(standing, is_blue=True)

        # update alliance standings
        for alliance in EveAllianceInfo.objects.filter(is_blue=True):
            if int(alliance.alliance_id) in standings:
                if float(standings[int(alliance.alliance_id)]['standing']) < float(settings.BLUE_STANDING):
                    logger.info("Alliance %s no longer meets minimum blue standing threshold" % alliance)
                    alliance.is_blue = False
                    alliance.save()
            elif alliance.alliance_id not in settings.STR_BLUE_ALLIANCE_IDS:
                logger.info("Alliance %s no longer in standings" % alliance)
                alliance.is_blue = False
                alliance.save()

        # update corp standings
        for corp in EveCorporationInfo.objects.filter(is_blue=True):
            if int(corp.corporation_id) in standings:
                if float(standings[int(corp.corporation_id)]['standing']) < float(settings.BLUE_STANDING):
                    logger.info("Corp %s no longer meets minimum blue standing threshold" % corp)
                    corp.is_blue = False
                    corp.save()
            elif corp.corporation_id not in settings.STR_BLUE_CORP_IDS:
                if corp.alliance:
                    if not corp.alliance.is_blue:
                        logger.info("Corp %s and its alliance %s are no longer blue" % (corp, corp.alliance))
                        corp.is_blue = False
                        corp.save()
                else:
                    logger.info("Corp %s is no longer blue" % corp)
                    corp.is_blue = False
                    corp.save()
    except evelink.api.APIError as e:
        logger.error("Model update failed with error code %s" % e.code)

    # delete unnecessary alliance models
    EveAllianceInfo.objects.filter(is_blue=False).exclude(alliance_id__in=settings.STR_ALLIANCE_IDS).delete()

    # delete unnecessary corp models
    EveCorporationInfo.objects.filter(is_blue=False).exclude(corporation_id__in=settings.STR_CORP_IDS).exclude(
        alliance__alliance_id__in=settings.STR_ALLIANCE_IDS).delete()
