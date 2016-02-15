from django.conf import settings
from celery.task import periodic_task
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from models import SyncGroupCache
from celery.task.schedules import crontab
from services.managers.openfire_manager import OpenfireManager
from services.managers.mumble_manager import MumbleManager
from services.managers.phpbb3_manager import Phpbb3Manager
from services.managers.ipboard_manager import IPBoardManager
from services.managers.teamspeak3_manager import Teamspeak3Manager
from services.managers.discord_manager import DiscordManager, DiscordAPIManager
from services.models import AuthTS
from services.models import TSgroup
from authentication.models import AuthServicesInfo
from eveonline.managers import EveManager
from services.managers.eve_api_manager import EveApiManager
from util.common_task import deactivate_services
from util import add_member_permission
from util import remove_member_permission
from util import check_if_user_has_permission
from util.common_task import add_user_to_group
from util.common_task import remove_user_from_group
from util.common_task import generate_corp_group_name
from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo
from authentication.managers import AuthServicesInfoManager
from services.models import DiscordAuthToken

import logging

logger = logging.getLogger(__name__)

def disable_member(user):
    logger.debug("Disabling member %s" % user)
    if user.user_permissions.all().exists():
        logger.info("Clearning user %s permission to deactivate user." % user)
        user.user_permissions.clear()
    if user.groups.all().exists():
        logger.info("Clearing user %s groups to deactivate user." % user)
        user.groups.clear()
    deactivate_services(user)

def is_teamspeak3_active():
    return settings.ENABLE_AUTH_TEAMSPEAK3 or settings.ENABLE_BLUE_TEAMSPEAK3

def update_jabber_groups(user):
    logger.debug("Updating jabber groups for user %s" % user)
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    logger.debug("User %s has %s syncgroups." % (user, len(syncgroups)))
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s jabber groups to %s" % (user, groups))

    OpenfireManager.update_user_groups(authserviceinfo.jabber_username, authserviceinfo.jabber_password, groups)
    logger.info("Updated user %s jabber groups." % user)


def update_mumble_groups(user):
    logger.debug("Updating mumble groups for user %s" % user)
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    logger.debug("User %s has %s syncgroups." % (user, len(syncgroups)))
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s mumble groups to %s" % (user, groups))
    MumbleManager.update_groups(authserviceinfo.mumble_username, groups)
    logger.info("Updated user %s mumble groups." % user)

def update_forum_groups(user):
    logger.debug("Updating forum groups for user %s" % user)
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    logger.debug("User %s has %s syncgroups." % (user, len(syncgroups)))
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s forum groups to %s" % (user, groups))
    Phpbb3Manager.update_groups(authserviceinfo.forum_username, groups)
    logger.info("Updated user %s forum groups." % user)

def update_ipboard_groups(user):
    logger.debug("Updating user %s ipboard groups." % user)
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    logger.debug("User %s has %s syncgroups." % (user, len(syncgroups)))
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s ipboard groups to %s" % (user, groups))
    IPBoardManager.update_groups(authserviceinfo.ipboard_username, groups)
    logger.info("Updated user %s ipboard groups." % user)

def update_teamspeak3_groups(user):
    logger.debug("Updating user %s teamspeak3 groups" % user)
    usergroups = user.groups.all()
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = {}
    for usergroup in usergroups:
        filtered_groups = AuthTS.objects.filter(auth_group=usergroup)
        if filtered_groups:
            for filtered_group in filtered_groups:
                for ts_group in filtered_group.ts_group.all():
                    groups[ts_group.ts_group_name] = ts_group.ts_group_id
    logger.debug("Updating user %s teamspeak3 groups to %s" % (user, groups))
    Teamspeak3Manager.update_groups(authserviceinfo.teamspeak3_uid, groups)
    logger.info("Updated user %s teamspeak3 groups." % user)

def update_discord_groups(user):
    logger.debug("Updating discord groups for user %s" % user)
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    logger.debug("User %s has %s syncgroups." % (user, len(syncgroups)))
    if len(groups) == 0:
        logger.debug("No syncgroups found for user. Adding empty group.")
        groups.append('empty')
    logger.debug("Updating user %s discord groups to %s" % (user, groups))
    DiscordManager.update_groups(authserviceinfo.discord_uid, groups)
    logger.info("Updated user %s discord groups." % user)

def create_syncgroup_for_user(user, groupname, servicename):
    logger.debug("Creating syncgroupcache for user %s group %s in service %s" % (user, groupname, servicename))
    synccache = SyncGroupCache()
    synccache.groupname = groupname
    synccache.user = user
    synccache.servicename = servicename
    synccache.save()
    logger.info("Created syncgroup for user %s group %s in service %s" % (user, groupname, servicename))


def remove_all_syncgroups_for_service(user, servicename):
    logger.debug("Removing all syncgroups for user %s service %s" % (user, servicename))
    syncgroups = SyncGroupCache.objects.filter(user=user)
    logger.debug("User %s has %s syncgroups." % (user, len(syncgroups)))
    for syncgroup in syncgroups:
        if syncgroup.servicename == servicename:
            logger.debug("Deleting syncgroups %s" % syncgroup)
            syncgroup.delete()
    logger.info("Removed all syncgroups for user %s service %s" % (user, servicename))


def add_to_databases(user, groups, syncgroups):
    logger.debug("add_to_database for user %s called. groups %s - syncgroups %s" % (user, groups, syncgroups))
    authserviceinfo = None
    try:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)
        logger.debug("Got authservicesinfo object %s" % authserviceinfo)
    except:
        logger.debug("No authservicesinfo object found for user %s" % user)
        pass

    if authserviceinfo:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)
		
	if authserviceinfo.teamspeak3_uid and authserviceinfo.teamspeak3_uid != "":
            logger.debug("Updating user TS groups.")
            update_teamspeak3_groups(user)
				
        for group in groups:
            if authserviceinfo.jabber_username and authserviceinfo.jabber_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="openfire").exists() is not True:
                    logger.debug("User %s has jabber username %s - missing group %s." % (user, authserviceinfo.jabber_username, group.name))
                    create_syncgroup_for_user(user, group.name, "openfire")
                    update_jabber_groups(user)
            if authserviceinfo.mumble_username and authserviceinfo.mumble_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="mumble").exists() is not True:
                    logger.debug("User %s has mumble username %s - missing group %s." % (user, authserviceinfo.mumble_username, group.name))
                    create_syncgroup_for_user(user, group.name, "mumble")
                    update_mumble_groups(user)
            if authserviceinfo.forum_username and authserviceinfo.forum_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="phpbb3").exists() is not True:
                    logger.debug("User %s has phpbb username %s - missing group %s." % (user, authserviceinfo.forum_username, group.name))
                    create_syncgroup_for_user(user, group.name, "phpbb3")
                    update_forum_groups(user)
            if authserviceinfo.ipboard_username and authserviceinfo.ipboard_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="ipboard").exists() is not True:
                    logger.debug("User %s has ipboard username %s - missing group %s." % (user, authserviceinfo.ipboard_username, group.name))
                    create_syncgroup_for_user(user, group.name, "ipboard")
                    update_ipboard_groups(user)
            if authserviceinfo.discord_uid and authserviceinfo.discord_uid != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="discord").exists() is not True:
                    logger.debug("User %s has discord uid %s - missing group %s." % (user, authserviceinfo.discord_uid, group.name))
                    create_syncgroup_for_user(user, group.name, "discord")
                    update_discord_groups(user)


def remove_from_databases(user, groups, syncgroups):
    logger.debug("remove_from_database for user %s called. groups %s - syncgroups %s" % (user, groups, syncgroups))
    authserviceinfo = None
    try:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)
        logger.debug("Got authservicesinfo object %s" % authserviceinfo)
    except:
        logger.debug("No authservicesinfo object found for user %s" % user)
        pass

    if authserviceinfo:
        update = False
        for syncgroup in syncgroups:
            group = groups.filter(name=syncgroup.groupname)
            logger.debug("Got group %s for syncgroup %s" % (group, syncgroup))
            if not group:
                logger.debug("Deleting syncgroup %s" % syncgroup)
                syncgroup.delete()
                update = True

        if update:
            logger.debug("Syncgroups updated. Propogating to services for user %s" % user)
            if authserviceinfo.jabber_username and authserviceinfo.jabber_username != "":
                logger.debug("User %s has jabber username %s - updating groups." % (user, authserviceinfo.jabber_username))
                update_jabber_groups(user)
            if authserviceinfo.mumble_username and authserviceinfo.mumble_username != "":
                logger.debug("User %s has mumble username %s - updating groups." % (user, authserviceinfo.mumble_username))
                update_mumble_groups(user)
            if authserviceinfo.forum_username and authserviceinfo.forum_username != "":
                logger.debug("User %s has forum username %s - updating groups." % (user, authserviceinfo.forum_username))
                update_forum_groups(user)
            if authserviceinfo.ipboard_username and authserviceinfo.ipboard_username != "":
                logger.debug("User %s has ipboard username %s - updating groups." % (user, authserviceinfo.ipboard_username))
                update_ipboard_groups(user)
            if authserviceinfo.teamspeak3_uid and authserviceinfo.teamspeak3_uid != "":
                logger.debug("User %s has ts3 uid %s - updating groups." % (user, authserviceinfo.teamspeak3_uid))
                update_teamspeak3_groups(user)
            if authserviceinfo.discord_uid and authserviceinfo.discord_uid != "":
                logger.debug("User %s has discord uid %s - updating groups." % (user, authserviceinfo.discord_uid))
                update_discord_groups(user)

def assign_corp_group(auth):
    corp_group = None
    if auth.main_char_id:
        if EveCharacter.objects.filter(character_id=auth.main_char_id).exists():
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
            corpname = generate_corp_group_name(char.corporation_name)
            state = determine_membership_by_character(char)
            if state == "BLUE" and settings.BLUE_CORP_GROUPS:
                logger.debug("Validating blue user %s has corp group assigned." % auth.user)
                corp_group, c = Group.objects.get_or_create(name=corpname)
            elif state == "MEMBER" and settings.MEMBER_CORP_GROUPS:
                logger.debug("Validating member %s has corp group assigned." % auth.user)
                corp_group, c = Group.objects.get_or_create(name=corpname)
            else:
                logger.debug("Ensuring non-member %s has no corp groups assigned." % auth.user)
    if corp_group:
        if not corp_group in auth.user.groups.all():
            logger.info("Adding user %s to corp group %s" % (auth.user, corp_group))
            auth.user.groups.add(corp_group)
    for g in auth.user.groups.all():
        if str.startswith(str(g.name), "Corp_"):
            if g != corp_group:
                logger.info("Removing user %s from old corpgroup %s" % (auth.user, g))
                auth.user.groups.remove(g)

def make_member(user):
    logger.debug("Ensuring user %s has member permissions and groups." % user)
    # ensure member is not blue right now
    if check_if_user_has_permission(user, 'blue_member'):
        logger.info("Removing user %s blue permission to transition to member" % user)
        remove_member_permission(user, 'blue_member')
    blue_group, c = Group.objects.get_or_create(name=settings.DEFAULT_BLUE_GROUP)
    if blue_group in user.groups.all():
        logger.info("Removing user %s blue group" % user)
        user.groups.remove(blue_group)
    # make member
    if check_if_user_has_permission(user, 'member') is False:
        logger.info("Adding user %s member permission" % user)
        add_member_permission(user, 'member')
    member_group, c = Group.objects.get_or_create(name=settings.DEFAULT_AUTH_GROUP)
    if not member_group in user.groups.all():
        logger.info("Adding user %s to member group" % user)
        user.groups.add(member_group)
    auth, c = AuthServicesInfo.objects.get_or_create(user=user)
    if auth.is_blue:
        logger.info("Marking user %s as non-blue" % user)
        auth.is_blue = False
        auth.save()
    assign_corp_group(auth)

def make_blue(user):
    logger.debug("Ensuring user %s has blue permissions and groups." % user)
    # ensure user is not a member
    if check_if_user_has_permission(user, 'member'):
        logger.info("Removing user %s member permission to transition to blue" % user)
        remove_member_permission(user, 'blue_member')
    member_group, c = Group.objects.get_or_create(name=settings.DEFAULT_AUTH_GROUP)
    if member_group in user.groups.all():
        logger.info("Removing user %s member group" % user)
        user.groups.remove(member_group)
    # make blue
    if check_if_user_has_permission(user, 'blue_member') is False:
        logger.info("Adding user %s blue permission" % user)
        add_member_permission(user, 'blue_member')
    blue_group, c = Group.objects.get_or_create(name=settings.DEFAULT_BLUE_GROUP)
    if not blue_group in user.groups.all():
        logger.info("Adding user %s to blue group" % user)
        user.groups.add(blue_group)
    auth, c = AuthServicesInfo.objects.get_or_create(user=user)
    if auth.is_blue is False:
        logger.info("Marking user %s as blue" % user)
        auth.is_blue = True
        auth.save()
    assign_corp_group(auth)

def determine_membership_by_character(char):
    if settings.IS_CORP:
        if char.corporation_id == settings.CORP_ID:
            logger.debug("Character %s in owning corp id %s" % (char, char.corporation_id))
            return "MEMBER"
    else:
        if char.alliance_id == settings.ALLIANCE_ID:
            logger.debug("Character %s in owning alliance id %s" % (char, char.alliance_id))
            return "MEMBER"
    if EveCorporationInfo.objects.filter(corporation_id=char.corporation_id).exists() is False:
         logger.debug("No corp model for character %s corp id %s. Unable to check standings. Non-member." % (char, char.corporation_id))
         return False
    else:
         corp = EveCorporationInfo.objects.get(corporation_id=char.corporation_id)
         if corp.is_blue:
             logger.debug("Character %s member of blue corp %s" % (char, corp))
             return "BLUE"
         else:
             logger.debug("Character %s member of non-blue corp %s. Non-member." % (char, corp))
             return False

def determine_membership_by_user(user):
    logger.debug("Determining membership of user %s" % user)
    auth, c = AuthServicesInfo.objects.get_or_create(user=user)
    if auth.main_char_id:
        if EveCharacter.objects.filter(character_id=auth.main_char_id).exists():
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
            return determine_membership_by_character(char)
        else:
            logger.debug("Character model matching user %s main character id %s does not exist. Non-member." % (user, auth.main_char_id))
            return False
    else:
        logger.debug("User %s has no main character set. Non-member." % user)
        return False

def set_state(user):
    state = determine_membership_by_user(user)
    logger.debug("Assigning user %s to state %s" % (user, state))
    if state == "MEMBER":
        make_member(user)
    elif state == "BLUE":
        make_blue(user)
    else:
        disable_member(user)

# Run every minute
@periodic_task(run_every=crontab(minute="*/1"))
def run_databaseUpdate():
    logger.debug("Starting database update.")
    users = User.objects.all()
    if (is_teamspeak3_active()):
        logger.debug("TS3 installed. Syncing local group objects.")
        Teamspeak3Manager._sync_ts_group_db()
    for user in users:
        logger.debug("Initiating database update for user %s" % user)
        groups = user.groups.all()
        logger.debug("User has groups %s" % groups)
        syncgroups = SyncGroupCache.objects.filter(user=user)
        logger.debug("User has syncgroups %s" % syncgroups)
        add_to_databases(user, groups, syncgroups)
        remove_from_databases(user, groups, syncgroups)

# Run every 2 hours
@periodic_task(run_every=crontab(minute="0", hour="*/2"))
def run_discord_token_cleanup():
    logger.debug("Running validation of all DiscordAuthTokens")
    for auth in DiscordAuthToken.objects.all():
        logger.debug("Testing DiscordAuthToken %s" % auth)
        if DiscordAPIManager.validate_token(auth.token):
            logger.debug("Token passes validation. Retaining %s" % auth)
        else:
            logger.debug("DiscordAuthToken failed validation. Deleting %s" % auth)
            auth.delete()

def refresh_api(api_key_pair):
    logger.debug("Running update on api key %s" % api_key_pair.api_id)
    user = api_key_pair.user
    if EveApiManager.api_key_is_valid(api_key_pair.api_id, api_key_pair.api_key):
        #check to ensure API key meets min spec
        logger.info("Determined api key %s is still active." % api_key_pair.api_id)
        still_valid = True
        state = determine_membership_by_user(user)
        if state == "BLUE":
            if settings.BLUE_API_ACCOUNT:
                type = EveApiManager.check_api_is_type_account(api_key_pair.api_id, api_key_pair.api_key)
                if type == None:
                    api_key_pair.error_count += 1
                    api_key_pair.save()
                    logger.info("API key %s incurred an error checking if type account. Error count is now %s" % (api_key_pair.api_id, api_key_pair.error_count))
                    still_valid = None
                elif type == False:
                    logger.info("Determined api key %s for blue user %s is no longer type account as requred." % (api_key_pair.api_id, user))
                    still_valid = False
                full = EveApiManager.check_blue_api_is_full(api_key_pair.api_id, api_key_pair.api_key)
                if full == None:
                    api_key_pair.error_count += 1
                    api_key_pair.save()
                    logger.info("API key %s incurred an error checking if meets mask requirements. Error count is now %s" % (api_key_pair.api_id, api_key_pair.error_count))
                    still_valid = None
                elif full == False:
                    logger.info("Determined api key %s for blue user %s no longer meets minimum access mask as required." % (api_key_pair.api_id, user))
                    still_valid = False
        elif state == "MEMBER":
            if settings.MEMBER_API_ACCOUNT:
                type = EveApiManager.check_api_is_type_account(api_key_pair.api_id, api_key_pair.api_key)
                if type == None:
                    api_key_pair.error_count += 1
                    api_key_pair.save()
                    logger.info("API key %s incurred an error checking if type account. Error count is now %s" % (api_key_pair.api_id, api_key_pair.error_count))
                    still_valid = None
                elif type == False:
                    logger.info("Determined api key %s for user %s is no longer type account as required." % (api_key_pair.api_id, user))
                    still_valid = False
                full = EveApiManager.check_api_is_full(api_key_pair.api_id, api_key_pair.api_key)
                if full == None:
                    api_key_pair.error_count += 1
                    api_key_pair.save()
                    logger.info("API key %s incurred an error checking if meets mask requirements. Error count is now %s" % (api_key_pair.api_id, api_key_pair.error_count))
                    still_valid = None
                elif full == False:
                    logger.info("Determined api key %s for user %s no longer meets minimum access mask as required." % (api_key_pair.api_id, user))
                    still_valid = False
        if still_valid == None:
               if api_key_pair.error_count >= 3:
                   logger.info("API key %s has incurred 3 or more errors. Assuming invalid." % api_key_pair.api_id)
                   still_valid = False
        if still_valid == False:
               logger.debug("API key %s has failed validation; it and its characters will be deleted." % api_key_pair.api_id)
               EveManager.delete_characters_by_api_id(api_key_pair.api_id, user.id)
               EveManager.delete_api_key_pair(api_key_pair.api_id, user.id)
        elif still_valid == True:
               if api_key_pair.error_count != 0:
                   logger.info("Clearing error count for api %s as it passed validation" % api_key_pair.api_id)
                   api_key_pair.error_count = 0
                   api_key_pair.save()
               logger.info("Determined api key %s still meets requirements." % api_key_pair.api_id)
               # Update characters
               characters = EveApiManager.get_characters_from_api(api_key_pair.api_id, api_key_pair.api_key)
               EveManager.update_characters_from_list(characters)
               new_character = False
               for char in characters.result:
                   # Ensure we have a model for all characters on key
                   if not EveManager.check_if_character_exist(characters.result[char]['name']):
                       new_character = True
                       logger.debug("API key %s has a new character on the account: %s" % (api_key_pair.api_id, characters.result[char]['name']))
                   if new_character:
                       logger.debug("Creating new character %s from api key %s" % (characters.result[char]['name'], api_key_pair.api_id))
                       EveManager.create_characters_from_list(characters, user, api_key_pair.api_key)
    else:
        logger.debug("API key %s is no longer valid; it and its characters will be deleted." % api_key_pair.api_id)
        EveManager.delete_characters_by_api_id(api_key_pair.api_id, user.id)
        EveManager.delete_api_key_pair(api_key_pair.api_id, user.id)

# Run every 3 hours
@periodic_task(run_every=crontab(minute=0, hour="*/3"))
def run_api_refresh():
    users = User.objects.all()
    logger.debug("Running api refresh on %s users." % len(users))
    for user in users:
        # Check if the api server is online
        logger.debug("Running api refresh for user %s" % user)
        if EveApiManager.check_if_api_server_online():
            api_key_pairs = EveManager.get_api_key_pairs(user.id)
            logger.debug("User %s has api key pairs %s" % (user, api_key_pairs))
            if api_key_pairs:
                authserviceinfo, c = AuthServicesInfo.objects.get_or_create(user=user)
                logger.debug("User %s has api keys. Proceeding to refresh." % user)
                for api_key_pair in api_key_pairs:
                    refresh_api(api_key_pair)
                # Check our main character
                if EveCharacter.objects.filter(character_id=authserviceinfo.main_char_id).exists() is False:
                    logger.info("User %s main character id %s missing model. Clearning main character." % (user, authserviceinfo.main_char_id))
                    authserviceinfo.main_char_id = ''
                    authserviceinfo.save()
        set_state(user)

def populate_alliance(id, blue=False):
    logger.info("Populating alliance model with id %s blue %s" % (id, blue))
    alliance_info = EveApiManager.get_alliance_information(id)

    if not alliance_info:
        raise ValueError("Supplied alliance id %s is invalid" % id)

    if EveAllianceInfo.objects.filter(alliance_id=id).exists():
        alliance = EveAllianceInfo.objects.get(alliance_id=id)
    else:
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

# Run Every 2 hours
@periodic_task(run_every=crontab(minute=0, hour="*/2"))
def run_corp_update():
    if EveApiManager.check_if_api_server_online() is False:
        logger.warn("Aborted updating corp and alliance models: API server unreachable")
        return
    standing_level = 'alliance'

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
            EveManager.update_alliance_info(ownerallianceinfo['id'], ownerallianceinfo['executor_id'], ownerallianceinfo['member_count'], False)
        else:
            populate_alliance(alliance_id)
        alliance = EveAllianceInfo.objects.get(alliance_id=alliance_id)

    # create corp info for owning corp if required
    if ownercorpinfo:
        if EveCorporationInfo.objects.filter(corporation_id=ownercorpinfo['id']).exists():
            logger.debug("Updating existing owner corp model with id %s" % ownercorpinfo['id'])
            EveManager.update_corporation_info(ownercorpinfo['id'], ownercorpinfo['members']['current'], alliance, False)
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

    # update existing alliance models
    for alliance in EveAllianceInfo.objects.all():
        logger.debug("Updating alliance %s" % alliance)
        allianceinfo = EveApiManager.get_alliance_information(alliance.alliance_id)
        if allianceinfo:
            EveManager.update_alliance_info(allianceinfo['id'], allianceinfo['executor_id'],
                                            allianceinfo['member_count'], alliance.is_blue)
            for corp in EveCorporationInfo.objects.filter(alliance=alliance):
                if corp.corporation_id in allianceinfo['member_corps'] is False:
                    logger.info("Corp %s no longer in alliance %s" % (corp, alliance))
                    corp.alliance = None
                    corp.save()
            populate_alliance(alliance.alliance_id, blue=alliance.is_blue)
        elif EveApiManager.check_if_alliance_exists(alliance.alliance_id) is False:
            logger.info("Alliance %s has closed. Deleting model" % alliance)
            alliance.delete()

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
                if corp.alliance.is_blue is False:
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
        if settings.IS_CORP is False:
            if alliance.alliance_id == settings.ALLIANCE_ID is False:
                logger.info("Deleting unnecessary alliance model %s" % alliance)
                alliance.delete()
        else:
            if alliance.evecorporationinfo_set.filter(corporation_id=settings.CORP_ID).exists() is False:
                logger.info("Deleting unnecessary alliance model %s" % alliance)
                alliance.delete()

    # delete unnecessary corp models
    for corp in EveCorporationInfo.objects.filter(is_blue=False):
        logger.debug("Checking to delete corp %s" % corp)
        if settings.IS_CORP is False:
            if corp.alliance:
                logger.debug("Corp %s has alliance %s" % (corp, corp.alliance))
                if corp.alliance.alliance_id == settings.ALLIANCE_ID is False:
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
                    if corp.alliance.evecorporationinfo_set.filter(corporation_id=settings.CORP_ID).exists() is False:
                        logger.info("Deleting unnecessary corp model %s" % corp)
                        corp.delete()
                else:
                    logger.info("Deleting unnecessary corp model %s" % corp)
                    corp.delete()
            else:
                logger.debug("Corp %s is owning corp" % corp)
