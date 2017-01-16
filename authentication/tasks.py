from __future__ import unicode_literals
from services.tasks import validate_services
from django.contrib.auth.models import Group
from authentication.models import AuthServicesInfo
from authentication.states import MEMBER_STATE, BLUE_STATE, NONE_STATE
from eveonline.models import EveCharacter, EveCorporationInfo
from notifications import notify
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_corp_group_name(corpname):
    return 'Corp_' + corpname.replace(' ', '_')


def generate_alliance_group_name(alliancename):
    return 'Alliance_' + alliancename.replace(' ', '_')


def disable_member(user):
    logger.debug("Disabling member %s" % user)
    if user.user_permissions.all().exists():
        logger.info("Clearning user %s permission to deactivate user." % user)
        user.user_permissions.clear()
    if user.groups.all().exists():
        logger.info("Clearing user %s groups to deactivate user." % user)
        user.groups.clear()
    validate_services(user, None)


def make_member(auth):
    logger.debug("Ensuring user %s has member permissions and groups." % auth.user)
    # ensure member is not blue right now
    blue_group, c = Group.objects.get_or_create(name=settings.DEFAULT_BLUE_GROUP)
    if blue_group in auth.user.groups.all():
        logger.info("Removing user %s blue group" % auth.user)
        auth.user.groups.remove(blue_group)
    # make member
    member_group, c = Group.objects.get_or_create(name=settings.DEFAULT_AUTH_GROUP)
    if member_group not in auth.user.groups.all():
        logger.info("Adding user %s to member group" % auth.user)
        auth.user.groups.add(member_group)
    assign_corp_group(auth)
    assign_alliance_group(auth)


def make_blue(auth):
    logger.debug("Ensuring user %s has blue permissions and groups." % auth.user)
    # ensure user is not a member
    member_group, c = Group.objects.get_or_create(name=settings.DEFAULT_AUTH_GROUP)
    if member_group in auth.user.groups.all():
        logger.info("Removing user %s member group" % auth.user)
        auth.user.groups.remove(member_group)
    # make blue
    blue_group, c = Group.objects.get_or_create(name=settings.DEFAULT_BLUE_GROUP)
    if blue_group not in auth.user.groups.all():
        logger.info("Adding user %s to blue group" % auth.user)
        auth.user.groups.add(blue_group)
    assign_corp_group(auth)
    assign_alliance_group(auth)


def determine_membership_by_character(char):
    if str(char.corporation_id) in settings.STR_CORP_IDS:
        logger.debug("Character %s in member corp id %s" % (char, char.corporation_id))
        return MEMBER_STATE
    elif str(char.alliance_id) in settings.STR_ALLIANCE_IDS:
        logger.debug("Character %s in member alliance id %s" % (char, char.alliance_id))
        return MEMBER_STATE
    elif not EveCorporationInfo.objects.filter(corporation_id=char.corporation_id).exists():
        logger.debug("No corp model for character %s corp id %s. Unable to check standings. Non-member." % (
            char, char.corporation_id))
        return NONE_STATE
    else:
        corp = EveCorporationInfo.objects.get(corporation_id=char.corporation_id)
        if corp.is_blue:
            logger.debug("Character %s member of blue corp %s" % (char, corp))
            return BLUE_STATE
        else:
            logger.debug("Character %s member of non-blue corp %s. Non-member." % (char, corp))
            return NONE_STATE


def determine_membership_by_user(user):
    logger.debug("Determining membership of user %s" % user)
    auth = AuthServicesInfo.objects.get(user=user)
    if auth.main_char_id:
        if EveCharacter.objects.filter(character_id=auth.main_char_id).exists():
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
            return determine_membership_by_character(char)
        else:
            logger.debug("Character model matching user %s main character id %s does not exist. Non-member." % (
                user, auth.main_char_id))
            return NONE_STATE
    else:
        logger.debug("User %s has no main character set. Non-member." % user)
        return NONE_STATE


def set_state(user):
    if user.is_active:
        state = determine_membership_by_user(user)
    else:
        state = NONE_STATE
    logger.debug("Assigning user %s to state %s" % (user, state))
    auth = AuthServicesInfo.objects.get(user=user)
    if auth.state != state:
        auth.state = state
        auth.save()
        notify(user, "Membership State Change", message="You membership state has been changed to %s" % state)
    assign_corp_group(auth)
    assign_alliance_group(auth)


def assign_corp_group(auth):
    corp_group = None
    if auth.main_char_id:
        if EveCharacter.objects.filter(character_id=auth.main_char_id).exists():
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
            corpname = generate_corp_group_name(char.corporation_name)
            if auth.state == BLUE_STATE and settings.BLUE_CORP_GROUPS:
                logger.debug("Validating blue user %s has corp group assigned." % auth.user)
                corp_group, c = Group.objects.get_or_create(name=corpname)
            elif auth.state == MEMBER_STATE and settings.MEMBER_CORP_GROUPS:
                logger.debug("Validating member %s has corp group assigned." % auth.user)
                corp_group, c = Group.objects.get_or_create(name=corpname)
            else:
                logger.debug("Ensuring %s has no corp groups assigned." % auth.user)
    if corp_group:
        if corp_group not in auth.user.groups.all():
            logger.info("Adding user %s to corp group %s" % (auth.user, corp_group))
            auth.user.groups.add(corp_group)
    for g in auth.user.groups.all():
        if str.startswith(str(g.name), "Corp_"):
            if g != corp_group:
                logger.info("Removing user %s from old corpgroup %s" % (auth.user, g))
                auth.user.groups.remove(g)


def assign_alliance_group(auth):
    alliance_group = None
    if auth.main_char_id:
        if EveCharacter.objects.filter(character_id=auth.main_char_id).exists():
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
            if char.alliance_name:
                alliancename = generate_alliance_group_name(char.alliance_name)
                if auth.state == BLUE_STATE and settings.BLUE_ALLIANCE_GROUPS:
                    logger.debug("Validating blue user %s has alliance group assigned." % auth.user)
                    alliance_group, c = Group.objects.get_or_create(name=alliancename)
                elif auth.state == MEMBER_STATE and settings.MEMBER_ALLIANCE_GROUPS:
                    logger.debug("Validating member %s has alliance group assigned." % auth.user)
                    alliance_group, c = Group.objects.get_or_create(name=alliancename)
                else:
                    logger.debug("Ensuring %s has no alliance groups assigned." % auth.user)
            else:
                logger.debug("User %s main character %s not in an alliance. Ensuring no alliance group assigned." % (
                    auth.user, char))
    if alliance_group:
        if alliance_group not in auth.user.groups.all():
            logger.info("Adding user %s to alliance group %s" % (auth.user, alliance_group))
            auth.user.groups.add(alliance_group)
    for g in auth.user.groups.all():
        if str.startswith(str(g.name), "Alliance_"):
            if g != alliance_group:
                logger.info("Removing user %s from old alliance group %s" % (auth.user, g))
                auth.user.groups.remove(g)
