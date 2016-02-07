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
    if auth.main_character_id:
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
                    logger.debug("Running update on api key %s" % api_key_pair.api_id)
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
                # Check our main character
                if EveCharacter.objects.filter(character_id=authserviceinfo.main_char_id).exists() is False:
                    logger.info("User %s main character id %s missing model. Clearning main character." % (user, authserviceinfo.main_char_id))
                    authserviceinfo.main_char_id = ''
                    authserviceinfo.save()
        set_state(user)


# Run Every 2 hours
@periodic_task(run_every=crontab(minute=0, hour="*/2"))
def run_corp_update():
    # I am not proud of this block of code
    if EveApiManager.check_if_api_server_online():
        logger.debug("API server online and reachable. Proceeding with corp update.")
        if settings.IS_CORP:
            # Create the corp
            logger.debug("Ensuring corp model exists for owning corp id %s due to settings.IS_CORP %s" % (settings.CORP_ID, settings.IS_CORP))
            ownercorpinfo = EveApiManager.get_corporation_information(settings.CORP_ID)
            logger.debug("Determined ownercorp info: %s" % ownercorpinfo)
            if not EveManager.check_if_corporation_exists_by_id(ownercorpinfo['id']):
                logger.debug("Owning corp id %s does not have a model. Creating." % ownercorpinfo['id'])
                if ownercorpinfo['alliance']['id'] is None:
                    logger.debug("Owning corp does not have an alliance. Creating model with alliance=None")
                    EveManager.create_corporation_info(ownercorpinfo['id'], ownercorpinfo['name'], ownercorpinfo['ticker'],
                                                       ownercorpinfo['members']['current'], False, None)
                else:
                    alliance_info = EveApiManager.get_alliance_information(ownercorpinfo['alliance']['id'])
                    logger.debug("Owning corp has an alliance, got info: %s" % alliance_info)
                    if not EveManager.check_if_alliance_exists_by_id(ownercorpinfo['alliance']['id']):
                        logger.debug("Owning corp missing alliance model. Creating for id %s" % ownercorpinfo['alliance']['id'])
                        EveManager.create_alliance_info(ownercorpinfo['alliance']['id'], alliance_info['name'], alliance_info['ticker'],
                                                        alliance_info['executor_id'], alliance_info['member_count'], False)
                    alliance = EveManager.get_alliance_info_by_id(ownercorpinfo['alliance']['id'])
                    logger.debug("Got alliance model %s for owning corp. Creating corp model." % alliance)
                    EveManager.create_corporation_info(ownercorpinfo['id'], ownercorpinfo['name'], ownercorpinfo['ticker'],
                                                       ownercorpinfo['members']['current'], False, alliance)

        else:
            # Updated alliance info
            logger.debug("Getting info for owning alliance %s" % settings.ALLIANCE_ID)
            alliance_info = EveApiManager.get_alliance_information(settings.ALLIANCE_ID)
            logger.debug("Owning alliance info: %s" % alliance_info)
             # Populate alliance info
            if not EveManager.check_if_alliance_exists_by_id(settings.ALLIANCE_ID):
                logger.debug("Missing alliance model for owning alliance. Creating with id %s" % settings.ALLIANCE_ID)
                EveManager.create_alliance_info(settings.ALLIANCE_ID, alliance_info['name'], alliance_info['ticker'],
                                             alliance_info['executor_id'], alliance_info['member_count'], False)
            alliance = EveManager.get_alliance_info_by_id(settings.ALLIANCE_ID)
            logger.debug("Got owning alliance model %s" % alliance)
            # Create the corps in the alliance
            for alliance_corp in alliance_info['member_corps']:
                corpinfo = EveApiManager.get_corporation_information(alliance_corp)
                logger.debug("Got corpinfo for alliance member corp: %s" % corpinfo)
                if not EveManager.check_if_corporation_exists_by_id(corpinfo['id']):
                    logger.debug("Alliance member corp id %s missing model - creating." % corpinfo['id'])
                    EveManager.create_corporation_info(corpinfo['id'], corpinfo['name'], corpinfo['ticker'],
                                                    corpinfo['members']['current'], False, alliance)

        #determine what level of standings to check
        #refer to https://github.com/eve-val/evelink/blob/master/evelink/parsing/contact_list.py#L43
        standing_level = 'alliance'
        if settings.IS_CORP:
            logger.debug("Switching standings check to corp level.")
            standing_level = 'corp'

        # Create the corps in the standings
        corp_standings = EveApiManager.get_corp_standings()
        logger.debug("Got %s corp standings." % len(corp_standings))
        if corp_standings:
            for standing_id in EveApiManager.get_corp_standings()[standing_level]:
                logger.debug("Processing standing id %s" % standing_id)
                if int(corp_standings[standing_level][standing_id]['standing']) >= settings.BLUE_STANDING:
                    logger.debug("Standing %s meets or exceeds blue threshold." % standing_id)
                    if EveApiManager.check_if_id_is_character(standing_id):
                        logger.debug("Standing id %s is a character. Not creating model.")
                        pass
                    elif EveApiManager.check_if_id_is_corp(standing_id):
                        corpinfo = EveApiManager.get_corporation_information(standing_id)
                        logger.debug("Standing id %s is a corp. Got corpinfo: %s" % (standing_id, corpinfo))
                        if not EveManager.check_if_corporation_exists_by_id(standing_id):
                            logger.debug("Corp model for standing id %s does not exist. Creating" % standing_id)
                            EveManager.create_corporation_info(corpinfo['id'], corpinfo['name'], corpinfo['ticker'],
                                                               corpinfo['members']['current'], True, None)
                    else:
                        # Alliance id create corps
                        blue_alliance_info = EveApiManager.get_alliance_information(standing_id)
                        logger.debug("Standing id %s is alliance. Got alliance info: %s" % (standing_id, blue_alliance_info))
                        if not EveManager.check_if_alliance_exists_by_id(standing_id):
                            logger.debug("Alliance model for standing id %s does not exist. Creating" % standing_id)
                            EveManager.create_alliance_info(standing_id, blue_alliance_info['name'],
                                                            blue_alliance_info['ticker'],
                                                            blue_alliance_info['executor_id'],
                                                            blue_alliance_info['member_count'], True)

                        blue_alliance = EveManager.get_alliance_info_by_id(standing_id)
                        logger.debug("Got alliance model %s for standing id %s" % (blue_alliance, standing_id))
                        for blue_alliance_corp in blue_alliance_info['member_corps']:
                            blue_info = EveApiManager.get_corporation_information(blue_alliance_corp)
                            logger.debug("Got corpinfo for member corp id %s of blue alliance %s: %s" % (blue_info['id'], blue_alliance, blue_info))
                            if not EveManager.check_if_corporation_exists_by_id(blue_info['id']):
                                logger.debug("Blue alliance %s member corp id %s missing model. Creating." % (blue_alliance, blue_info['id']))
                                EveManager.create_corporation_info(blue_info['id'], blue_info['name'],
                                                                   blue_info['ticker'],
                                                                   blue_info['members']['current'], True, blue_alliance)

            # Update all allinace info's
            for all_alliance_info in EveManager.get_all_alliance_info():
                logger.debug("Validating alliance model %s" % all_alliance_info)
                if EveApiManager.check_if_alliance_exists(all_alliance_info.alliance_id):
                    all_alliance_api_info = EveApiManager.get_alliance_information(all_alliance_info.alliance_id)
                    logger.debug("Got alliance %s alliance info: %s" % (all_alliance_info, all_alliance_api_info))
                    if (not settings.IS_CORP and all_alliance_info.alliance_id == settings.ALLIANCE_ID):
                        logger.debug("Alliance %s is owning alliance. Updating info." % all_alliance_info)
                        EveManager.update_alliance_info(all_alliance_api_info['id'], all_alliance_api_info['executor_id'],
                                                        all_alliance_api_info['member_count'], False)
                    elif standing_level in corp_standings:
                        if int(all_alliance_info.alliance_id) in corp_standings[standing_level]:
                            if int(corp_standings[standing_level][int(all_alliance_info.alliance_id)][
                                'standing']) >= settings.BLUE_STANDING:
                                logger.debug("Alliance %s is blue. Updating." % all_alliance_info)
                                EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                                all_alliance_api_info['executor_id'],
                                                                all_alliance_api_info['member_count'], True)
                            else:
                                logger.debug("Alliance %s does not meet blue standing threshold. Updating as non-blue." % all_alliance_info)
                                EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                                all_alliance_api_info['executor_id'],
                                                                all_alliance_api_info['member_count'], False)
                        else:
                            logger.debug("Alliance %s not in standings. Updating as non-blue." % all_alliance_info)
                            EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                            all_alliance_api_info['executor_id'],
                                                            all_alliance_api_info['member_count'], False)
                    else:
                        logger.debug("No standings found. Updating alliance %s as non-blue." % all_alliance_info)
                        EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                        all_alliance_api_info['executor_id'],
                                                        all_alliance_api_info['member_count'], False)
                else:
                    logger.info("Alliance %s has closed. Deleting model." % all_alliance_info)
                    #alliance no longer exists
                    all_alliance_info.delete()

            # Update corp infos
            for all_corp_info in EveManager.get_all_corporation_info():
                logger.debug("Validating corp model %s" % all_corp_info)
                if EveApiManager.check_if_corp_exists(all_corp_info.corporation_id):
                    alliance = None
                    corpinfo = EveApiManager.get_corporation_information(all_corp_info.corporation_id)
                    if corpinfo['alliance']['id'] is not None:
                        alliance = EveManager.get_alliance_info_by_id(corpinfo['alliance']['id'])
                    logger.debug("Got corpinfo %s and allianceinfo %s" % (corpinfo, alliance))

                    if (settings.IS_CORP and all_corp_info.corporation_id == settings.CORP_ID):
                        logger.debug("Corp %s is owning corp. Updating." % all_corp_info)
                        EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], None, False)
                    elif int(all_corp_info.corporation_id) in corp_standings[standing_level]:
                        if int(corp_standings[standing_level][int(all_corp_info.corporation_id)][
                            'standing']) >= settings.BLUE_STANDING:
                            logger.debug("Corp %s is blue. Updating." % all_corp_info)
                            EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], None, True)
                        else:
                            logger.debug("Corp %s does not meet blue standing threshold. Updating as non-blue." % all_corp_info)
                            EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], None, False)
                    elif alliance is not None and all_corp_info.alliance is not None:
                        logger.debug("Corp %s not in standings - checking alliance with model %s" % (all_corp_info, alliance))
                        if (not settings.IS_CORP) and (all_corp_info.alliance.alliance_id == settings.ALLIANCE_ID):
                            logger.debug("Corp %s is member of owning alliance. Updating." % all_corp_info)
                            EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance, False)
                        elif int(alliance.alliance_id) in corp_standings[standing_level]:
                            if int(corp_standings[standing_level][int(alliance.alliance_id)][
                                'standing']) >= settings.BLUE_STANDING:
                                logger.debug("Corp %s alliance %s is blue. Updating." % (all_corp_info, alliance))
                                EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance,
                                                                   True)
                            else:
                                logger.debug("Corp %s alliance %s does not meet blue standing threshold. Updating as non-blue." % (all_corp_info, alliance))
                                EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance,
                                                                   False)
                        else:
                            logger.debug("Corp %s alliance %s not found in standings. Updating as non-blue." % (all_corp_info, alliance))
                            EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance,
                                                               False)
                    else:
                        logger.info("Corp model %s is not owning, member of owning alliance, or in standings. Updating as non-blue." % all_corp_info)
                        EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], None, False)
                else:
                    #corp has closed
                    logger.info("Corp %s has closed. Deleting model." % all_corp_info)
                    all_corp_info.delete()

        # Remove irrelevent corp and alliance models
        # Check the corps
        for all_corp_info in EveManager.get_all_corporation_info():
            logger.debug("Checking to delete corp model %s" % all_corp_info)
            if settings.IS_CORP:
                if all_corp_info.corporation_id != settings.CORP_ID:
                    if not all_corp_info.is_blue:
                        logger.info("Corp model %s is not owning corp nor blue. Deleting." % all_corp_info)
                        all_corp_info.delete()
            else:
                if all_corp_info.alliance is not None:
                    if all_corp_info.alliance.alliance_id != settings.ALLIANCE_ID:
                        if not all_corp_info.is_blue:
                            logger.info("Corp model %s not in owning alliance nor blue. Deleting." % all_corp_info)
                            all_corp_info.delete()
                elif not all_corp_info.is_blue:
                    logger.info("Corp model %s has no alliance and is not blue. Deleting." % all_corp_info)
                    all_corp_info.delete()

        # Check the alliances
        for all_alliance_info in EveManager.get_all_alliance_info():
            logger.debug("Checking to delete alliance model %s" % all_alliance_info)
            if settings.IS_CORP:
                if all_alliance_info.is_blue is not True:
                    if ownercorpinfo['alliance']['id'] is not None:
                        if int(all_alliance_info.alliance_id) != ownercorpinfo['alliance']['id']:
                            logger.info("Alliance model %s not owning corp alliance nor blue. Deleting." % all_alliance_info)
                            all_alliance_info.delete()
                    else:
                        logger.info("Alliance model %s not blue to alliance-less owning corp. Deleting." % all_alliance_info)
                        all_alliance_info.delete()
            elif all_alliance_info.alliance_id != settings.ALLIANCE_ID:
                if all_alliance_info.is_blue is not True:
                    logger.info("Alliance model %s not owning alliance nor blue. Deleting." % all_alliance_info)
                    all_alliance_info.delete()
