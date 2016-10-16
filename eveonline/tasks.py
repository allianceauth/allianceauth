from __future__ import unicode_literals
from django.conf import settings
from celery.task import periodic_task
from django.contrib.auth.models import User
from notifications import notify
from celery import task
from celery.task.schedules import crontab
from authentication.models import AuthServicesInfo
from eveonline.managers import EveManager
from eveonline.models import EveApiKeyPair
from services.managers.eve_api_manager import EveApiManager
from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo
from authentication.tasks import set_state
import logging
import evelink

logger = logging.getLogger(__name__)


@task
def refresh_api(api):
    logger.debug('Running update on api key %s' % api.api_id)
    still_valid = True
    try:
        EveApiManager.validate_api(api.api_id, api.api_key, api.user)
        # Update characters
        characters = EveApiManager.get_characters_from_api(api.api_id, api.api_key)
        EveManager.update_characters_from_list(characters)
        new_character = False
        for char in characters.result:
            # Ensure we have a model for all characters on key
            if not EveManager.check_if_character_exist(characters.result[char]['name']):
                logger.debug(
                    "API key %s has a new character on the account: %s" % (api.api_id, characters.result[char]['name']))
                new_character = True
        if new_character:
            logger.debug("Creating new character %s from api key %s" % (characters.result[char]['name'], api.api_id))
            EveManager.create_characters_from_list(characters, api.user, api.api_id)
        current_chars = EveCharacter.objects.filter(api_id=api.api_id)
        for c in current_chars:
            if not int(c.character_id) in characters.result:
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
    finally:
        if not still_valid:
            EveManager.delete_characters_by_api_id(api.api_id, api.user.id)
            EveManager.delete_api_key_pair(api.api_id, api.user.id)
            notify(api.user, "API Key Deleted",
                   message="Your API key ID %s is invalid. It and its associated characters have been deleted." % api.api_id,
                   level="danger")


@task
def refresh_user_apis(user):
    logger.debug('Refreshing all APIs belonging to user %s' % user)
    apis = EveApiKeyPair.objects.filter(user=user)
    for x in apis:
        refresh_api(x)
    # Check our main character
    auth = AuthServicesInfo.objects.get_or_create(user=user)[0]
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


@periodic_task(run_every=crontab(minute=0, hour="*/3"))
def run_api_refresh():
    for u in User.objects.all():
        refresh_user_apis.delay(u)


def populate_alliance(id, blue=False):
    logger.debug("Populating alliance model with id %s blue %s" % (id, blue))
    alliance_info = EveApiManager.get_alliance_information(id)

    if not alliance_info:
        raise ValueError("Supplied alliance id %s is invalid" % id)

    if not EveAllianceInfo.objects.filter(alliance_id=id).exists():
        EveManager.create_alliance_info(alliance_info['id'], alliance_info['name'], alliance_info['ticker'],
                                        alliance_info['executor_id'], alliance_info['member_count'], blue)
    alliance = EveAllianceInfo.objects.get(alliance_id=id)
    for member_corp in alliance_info['member_corps']:
        if EveCorporationInfo.objects.filter(corporation_id=member_corp).exists():
            corp = EveCorporationInfo.objects.get(corporation_id=member_corp)
            if corp.alliance != alliance:
                corp.alliance = alliance
                corp.save()
        else:
            logger.info("Creating new alliance member corp id %s" % member_corp)
            corpinfo = EveApiManager.get_corporation_information(member_corp)
            EveManager.create_corporation_info(corpinfo['id'], corpinfo['name'], corpinfo['ticker'],
                                               corpinfo['members']['current'], blue, alliance)


@task
def update_alliance(id):
    alliance = EveAllianceInfo.objects.get(alliance_id=id)
    corps = EveCorporationInfo.objects.filter(alliance=alliance)
    logger.debug("Updating alliance %s with %s member corps" % (alliance, len(corps)))
    allianceinfo = EveApiManager.get_alliance_information(alliance.alliance_id)
    if allianceinfo:
        EveManager.update_alliance_info(allianceinfo['id'], allianceinfo['executor_id'],
                                        allianceinfo['member_count'], alliance.is_blue)
        for corp in corps:
            if corp.corporation_id in allianceinfo['member_corps'] is False:
                logger.info("Corp %s no longer in alliance %s" % (corp, alliance))
                corp.alliance = None
                corp.save()
        populate_alliance(alliance.alliance_id, blue=alliance.is_blue)
    elif EveApiManager.check_if_alliance_exists(alliance.alliance_id) is False:
        logger.info("Alliance %s has closed. Deleting model" % alliance)
        alliance.delete()


@task
def update_corp(id):
    corp = EveCorporationInfo.objects.get(corporation_id=id)
    logger.debug("Updating corp %s" % corp)
    corpinfo = EveApiManager.get_corporation_information(corp.corporation_id)
    if corpinfo:
        alliance = None
        if EveAllianceInfo.objects.filter(alliance_id=corpinfo['alliance']['id']).exists():
            alliance = EveAllianceInfo.objects.get(alliance_id=corpinfo['alliance']['id'])
        EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance, corp.is_blue)
    elif EveApiManager.check_if_corp_exists(corp.corporation_id) is False:
        logger.info("Corp %s has closed. Deleting model" % corp)
        corp.delete()

        # Run Every 2 hours


@periodic_task(run_every=crontab(minute=0, hour="*/2"))
def run_corp_update():
    if EveApiManager.check_if_api_server_online() is False:
        logger.warn("Aborted updating corp and alliance models: API server unreachable")
        return
    standing_level = 'alliance'
    try:
        # get corp info for owning corp if required
        ownercorpinfo = {}
        if settings.IS_CORP:
            standing_level = 'corp'
            logger.debug("Getting information for owning corp with id %s" % settings.CORP_ID)
            ownercorpinfo = EveApiManager.get_corporation_information(settings.CORP_ID)
            if not ownercorpinfo:
                logger.error("Failed to retrieve corp info for owning corp id %s - bad corp id?" % settings.CORP_ID)
                return

        # check if we need to update an alliance model
        alliance_id = ''
        if ownercorpinfo and ownercorpinfo['alliance']['id']:
            alliance_id = ownercorpinfo['alliance']['id']
        elif settings.IS_CORP is False:
            alliance_id = settings.ALLIANCE_ID

        # get and create alliance info for owning alliance if required
        alliance = None
        if alliance_id:
            logger.debug("Getting information for owning alliance with id %s" % alliance_id)
            ownerallianceinfo = EveApiManager.get_alliance_information(alliance_id)
            if not ownerallianceinfo:
                logger.error("Failed to retrieve corp info for owning alliance id %s - bad alliance id?" % alliance_id)
                return
            if EveAllianceInfo.objects.filter(alliance_id=ownerallianceinfo['id']).exists():
                logger.debug("Updating existing owner alliance model with id %s" % alliance_id)
                EveManager.update_alliance_info(ownerallianceinfo['id'], ownerallianceinfo['executor_id'],
                                                ownerallianceinfo['member_count'], False)
            else:
                populate_alliance(alliance_id)
                alliance = EveAllianceInfo.objects.get(alliance_id=alliance_id)

        # create corp info for owning corp if required
        if ownercorpinfo:
            if EveCorporationInfo.objects.filter(corporation_id=ownercorpinfo['id']).exists():
                logger.debug("Updating existing owner corp model with id %s" % ownercorpinfo['id'])
                EveManager.update_corporation_info(ownercorpinfo['id'], ownercorpinfo['members']['current'], alliance,
                                                   False)
            else:
                logger.info("Creating model for owning corp with id %s" % ownercorpinfo['id'])
                EveManager.create_corporation_info(ownercorpinfo['id'], ownercorpinfo['name'], ownercorpinfo['ticker'],
                                                   ownercorpinfo['members']['current'], False, alliance)

        # validate and create corp models for member corps of owning alliance
        if alliance:
            current_corps = EveCorporationInfo.objects.filter(alliance=alliance)
            for corp in current_corps:
                if corp.corporation_id in ownerallianceinfo['member_corps'] is False:
                    logger.info("Corp %s is no longer in owning alliance %s - updating model." % (corp, alliance))
                    corp.alliance = None
                    corp.save()
            for member_corp in ownerallianceinfo['member_corps']:
                if EveCorporationInfo.objects.filter(corporation_id=member_corp).exists():
                    corp = EveCorporationInfo.objects.get(corporation_id=member_corp)
                    if corp.alliance == alliance is not True:
                        logger.info("Associating corp %s with owning alliance %s" % (corp, alliance))
                        corp.alliance = alliance
                        corp.save()
                else:
                    corpinfo = EveApiManager.get_corporation_information(member_corp)
                    logger.info("Creating model for owning alliance member corp with id %s" % corpinfo['id'])
                    EveManager.create_corporation_info(corpinfo['id'], corpinfo['name'], corpinfo['ticker'],
                                                       corpinfo['members']['current'], False, alliance)

        # update existing corp models
        for corp in EveCorporationInfo.objects.all():
            update_corp.delay(corp.corporation_id)

        # update existing alliance models
        for alliance in EveAllianceInfo.objects.all():
            update_alliance.delay(alliance.alliance_id)

        # create standings
        standings = EveApiManager.get_corp_standings()
        if standings:
            standings = standings[standing_level]
            for standing in standings:
                if int(standings[standing]['standing']) >= settings.BLUE_STANDING:
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
                            populate_alliance(standing, blue=True)
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
                            corpinfo = EveApiManager.get_corporation_information(standing)
                            corp_alliance = None
                            if EveAllianceInfo.objects.filter(alliance_id=corpinfo['alliance']['id']).exists():
                                logger.debug("New corp model for standing %s has existing alliance model" % standing)
                                corp_alliance = EveAllianceInfo.objects.get(alliance_id=corpinfo['alliance']['id'])
                            EveManager.create_corporation_info(corpinfo['id'], corpinfo['name'], corpinfo['ticker'],
                                                               corpinfo['members']['current'], True, corp_alliance)

        # update alliance standings
        for alliance in EveAllianceInfo.objects.filter(is_blue=True):
            if int(alliance.alliance_id) in standings:
                if float(standings[int(alliance.alliance_id)]['standing']) < float(settings.BLUE_STANDING):
                    logger.info("Alliance %s no longer meets minimum blue standing threshold" % alliance)
                    alliance.is_blue = False
                    alliance.save()
            else:
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
            else:
                if corp.alliance:
                    if not corp.alliance.is_blue:
                        logger.info("Corp %s and its alliance %s are no longer blue" % (corp, corp.alliance))
                        corp.is_blue = False
                        corp.save()
                else:
                    logger.info("Corp %s is no longer blue" % corp)
                    corp.is_blue = False
                    corp.save()

        # delete unnecessary alliance models
        for alliance in EveAllianceInfo.objects.filter(is_blue=False):
            logger.debug("Checking to delete alliance %s" % alliance)
            if not settings.IS_CORP:
                if not alliance.alliance_id == settings.ALLIANCE_ID:
                    logger.info("Deleting unnecessary alliance model %s" % alliance)
                    alliance.delete()
            else:
                if not alliance.evecorporationinfo_set.filter(corporation_id=settings.CORP_ID).exists():
                    logger.info("Deleting unnecessary alliance model %s" % alliance)
                    alliance.delete()

        # delete unnecessary corp models
        for corp in EveCorporationInfo.objects.filter(is_blue=False):
            logger.debug("Checking to delete corp %s" % corp)
            if not settings.IS_CORP:
                if corp.alliance:
                    logger.debug("Corp %s has alliance %s" % (corp, corp.alliance))
                    if not corp.alliance.alliance_id == settings.ALLIANCE_ID:
                        logger.info("Deleting unnecessary corp model %s" % corp)
                        corp.delete()
                else:
                    logger.info("Deleting unnecessary corp model %s" % corp)
                    corp.delete()
            else:
                if corp.corporation_id != settings.CORP_ID:
                    logger.debug("Corp %s is not owning corp" % corp)
                    if corp.alliance:
                        logger.debug("Corp %s has alliance %s" % (corp, corp.alliance))
                        if not corp.alliance.evecorporationinfo_set.filter(corporation_id=settings.CORP_ID).exists():
                            logger.info("Deleting unnecessary corp model %s" % corp)
                            corp.delete()
                    else:
                        logger.info("Deleting unnecessary corp model %s" % corp)
                        corp.delete()
                else:
                    logger.debug("Corp %s is owning corp" % corp)
    except evelink.api.APIError as e:
        logger.error("Model update failed with error code %s" % e.code)
