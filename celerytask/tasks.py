from django.conf import settings
from celery.task import periodic_task
from django.contrib.auth.models import User

from models import SyncGroupCache
from celery.task.schedules import crontab
from services.managers.openfire_manager import OpenfireManager
from services.managers.mumble_manager import MumbleManager
from services.managers.phpbb3_manager import Phpbb3Manager
from services.managers.ipboard_manager import IPBoardManager
from services.managers.teamspeak3_manager import Teamspeak3Manager
from authentication.models import AuthServicesInfo
from eveonline.managers import EveManager
from services.managers.eve_api_manager import EveApiManager
from util.common_task import deactivate_services
from util import add_member_permission
from util import remove_member_permission
from util import check_if_user_has_permission
from util.common_task import add_user_to_group
from util.common_task import remove_user_from_group

def disable_alliance_member(user, char_id):
    remove_member_permission(user, 'member')
    remove_user_from_group(user, settings.DEFAULT_AUTH_GROUP)
    remove_user_from_group(user,
                           generate_corp_group_name(
                               EveManager.get_character_by_id(char_id).corporation_name))
    deactivate_services(user)

def disable_blue_member(user):
    remove_member_permission(user, 'blue_member')
    remove_user_from_group(user, settings.DEFAULT_BLUE_GROUP)
    deactivate_services(user)

def update_jabber_groups(user):
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []

    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')

    print groups

    OpenfireManager.update_user_groups(authserviceinfo.jabber_username, authserviceinfo.jabber_password, groups)


def update_mumble_groups(user):
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')

    MumbleManager.update_groups(authserviceinfo.mumble_username, groups)


def update_forum_groups(user):
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')

    Phpbb3Manager.update_groups(authserviceinfo.forum_username, groups)


def update_ipboard_groups(user):
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')

    IPBoardManager.update_groups(authserviceinfo.ipboard_username, groups)


def update_teamspeak3_groups(user):
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')

    Teamspeak3Manager.update_groups(authserviceinfo.teamspeak3_uid, groups)


def create_syncgroup_for_user(user, groupname, servicename):
    synccache = SyncGroupCache()
    synccache.groupname = groupname
    synccache.user = user
    synccache.servicename = servicename
    synccache.save()


def remove_all_syncgroups_for_service(user, servicename):
    syncgroups = SyncGroupCache.objects.filter(user=user)
    for syncgroup in syncgroups:
        if syncgroup.servicename == servicename:
            syncgroup.delete()


def add_to_databases(user, groups, syncgroups):
    authserviceinfo = None
    try:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)
    except:
        pass

    if authserviceinfo:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)

        for group in groups:

            if authserviceinfo.jabber_username and authserviceinfo.jabber_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="openfire").exists() is not True:
                    create_syncgroup_for_user(user, group.name, "openfire")
                    update_jabber_groups(user)
            if authserviceinfo.mumble_username and authserviceinfo.mumble_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="mumble").exists() is not True:
                    create_syncgroup_for_user(user, group.name, "mumble")
                    update_mumble_groups(user)
            if authserviceinfo.forum_username and authserviceinfo.forum_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="phpbb3").exists() is not True:
                    create_syncgroup_for_user(user, group.name, "phpbb3")
                    update_forum_groups(user)
            if authserviceinfo.ipboard_username and authserviceinfo.ipboard_username != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="ipboard").exists() is not True:
                    create_syncgroup_for_user(user, group.name, "ipboard")
                    update_ipboard_groups(user)
            if authserviceinfo.teamspeak3_uid and authserviceinfo.teamspeak3_uid != "":
                if syncgroups.filter(groupname=group.name).filter(servicename="teamspeak3").exists() is not True:
                    create_syncgroup_for_user(user, group.name, "teamspeak3")
                    update_teamspeak3_groups(user)


def remove_from_databases(user, groups, syncgroups):
    authserviceinfo = None
    try:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)
    except:
        pass

    if authserviceinfo:
        update = False
        for syncgroup in syncgroups:
            group = groups.filter(name=syncgroup.groupname)

            if not group:
                syncgroup.delete()
                update = True

        if update:
            if authserviceinfo.jabber_username and authserviceinfo.jabber_username != "":
                update_jabber_groups(user)
            if authserviceinfo.mumble_username and authserviceinfo.mumble_username != "":
                update_mumble_groups(user)
            if authserviceinfo.forum_username and authserviceinfo.forum_username != "":
                update_forum_groups(user)
            if authserviceinfo.ipboard_username and authserviceinfo.ipboard_username != "":
                update_ipboard_groups(user)
            if authserviceinfo.teamspeak3_uid and authserviceinfo.teamspeak3_uid != "":
                update_teamspeak3_groups(user)


# Run every minute
@periodic_task(run_every=crontab(minute="*/1"))
def run_databaseUpdate():
    users = User.objects.all()
    for user in users:
        groups = user.groups.all()
        syncgroups = SyncGroupCache.objects.filter(user=user)
        add_to_databases(user, groups, syncgroups)
        remove_from_databases(user, groups, syncgroups)


# Run every 3 hours
@periodic_task(run_every=crontab(minute=0, hour="*/3"))
def run_api_refresh():
    users = User.objects.all()

    for user in users:
        # Check if the api server is online
        if EveApiManager.check_if_api_server_online():
            api_key_pairs = EveManager.get_api_key_pairs(user.id)
            if api_key_pairs:
                valid_key = False
                authserviceinfo = AuthServicesInfo.objects.get(user=user)

                print 'Running update on user: ' + user.username
                if authserviceinfo.main_char_id:
                    if authserviceinfo.main_char_id != "":
                        for api_key_pair in api_key_pairs:
                            print 'Running on ' + api_key_pair.api_id + ':' + api_key_pair.api_key
                            if EveApiManager.api_key_is_valid(api_key_pair.api_id, api_key_pair.api_key):
                                # Update characters
                                characters = EveApiManager.get_characters_from_api(api_key_pair.api_id,
                                                                                   api_key_pair.api_key)
                                EveManager.update_characters_from_list(characters)
                                valid_key = True
                            else:
                                EveManager.delete_characters_by_api_id(api_key_pair.api_id, user)
                                EveManager.delete_api_key_pair(api_key_pair.api_id, api_key_pair.api_key)

                        if valid_key:
                            # Check our main character
                            character = EveManager.get_character_by_id(authserviceinfo.main_char_id)
                            corp = EveManager.get_corporation_info_by_id(character.corporation_id)
                            main_corp_id = EveManager.get_charater_corporation_id_by_id(authserviceinfo.main_char_id)
                            if main_corp_id == settings.CORP_ID:
                                if not check_if_user_has_permission(user, "member"):
                                    #transition from blue to member
                                    if check_if_user_has_permission(user, "blue_member"):
                                        #strip blue status
                                        remove_member_permission(user, "blue_member")
                                        remove_user_from_group(settings.DEFAULT_BLUE_GROUP)
                                    add_member_permission(user, "member")
                                    add_user_to_group(user, settings.DEFAULT_AUTH_GROUP)
                            elif corp is not None:
                                if corp.is_blue is not True:
                                    if check_if_user_has_permission(user, "member"):
                                        disable_alliance_member(user, authserviceinfo.main_char_id)
                                    elif check_if_user_has_permission(user, "blue_member"):
                                        disable_blue_member(user)
                                    else:
                                        deactivate_services(user)
                                else:
                                    if check_if_user_has_permission(user, "member"):
                                        remove_member_permission(user, "member")
                                        remove_user_from_group(user, settings.DEFAULT_AUTH_GROUP)
                                    if not check_if_user_has_permission(user, "blue_member"):
                                        add_member_permission(user, "blue_member")
                                        add_user_to_group(user, settings.DEFAULT_BLUE_GROUP)

                                    #Fix mumble username ticker
                                    MumbleManager.delete_user(authserviceinfo.mumble_username)
                                    remove_all_syncgroups_for_service(user, "mumble")
                                    AuthServicesInfoManager.update_user_mumble_info("", "", request.user)

                                    #make new user (how generous)
                                    result = MumbleManager.create_blue_user(character.corporation_ticker, character.character_name)
                                    AuthServicesInfoManager.update_user_mumble_info(result[0], result[1], user)
                                    update_mumble_groups(request.user)
                            else:
                                if check_if_user_has_permission(user, "member"):
                                    disable_alliance_member(user, authserviceinfo.main_char_id)
                                elif check_if_user_has_permission(user, "blue_member"):
                                    disable_blue_member(user, authserviceonfo.main_char_id)
                                else:
                                    deactivate_services(user)

                        else:
                            # nuke it
                            if check_if_user_has_permission(user, "member"):
                                disable_alliance_member(user, authserviceinfo.main_char_id)
                            elif check_if_user_has_permission(user, "blue_member"):
                                disable_blue_member(user)
                            else:
                                deactivate_services(user)

                else:
                    print 'No main_char_id set'


# Run Every 2 hours
@periodic_task(run_every=crontab(minute=0, hour="*/2"))
def run_corp_update():
    # I am not proud of this block of code
    if EveApiManager.check_if_api_server_online():

        # Create the corp
        corpinfo = EveApiManager.get_corporation_information(settings.CORP_ID)
        if not EveManager.check_if_corporation_exists_by_id(corpinfo['id']):
            EveManager.create_corporation_info(corpinfo['id'], corpinfo['name'], corpinfo['ticker'],
                                               corpinfo['members']['current'], False, None)

        # Create the corps in the standings
        corp_standings = EveApiManager.get_corp_standings()
        if corp_standings:
            for standing_id in EveApiManager.get_corp_standings()['alliance']:
                if int(corp_standings['alliance'][standing_id]['standing']) >= settings.BLUE_STANDING:
                    if EveApiManager.check_if_id_is_character(standing_id):
                        pass
                    elif EveApiManager.check_if_id_is_corp(standing_id):
                        corpinfo = EveApiManager.get_corporation_information(standing_id)
                        if not EveManager.check_if_corporation_exists_by_id(standing_id):
                            EveManager.create_corporation_info(corpinfo['id'], corpinfo['name'], corpinfo['ticker'],
                                                               corpinfo['members']['current'], True, None)
                    else:
                        # Alliance id create corps
                        blue_alliance_info = EveApiManager.get_alliance_information(standing_id)

                        if not EveManager.check_if_alliance_exists_by_id(standing_id):
                            EveManager.create_alliance_info(standing_id, blue_alliance_info['name'],
                                                            blue_alliance_info['ticker'],
                                                            blue_alliance_info['executor_id'],
                                                            blue_alliance_info['member_count'], True)

                        blue_alliance = EveManager.get_alliance_info_by_id(standing_id)

                        for blue_alliance_corp in blue_alliance_info['member_corps']:
                            blue_info = EveApiManager.get_corporation_information(blue_alliance_corp)
                            if not EveManager.check_if_corporation_exists_by_id(blue_info['id']):
                                EveManager.create_corporation_info(blue_info['id'], blue_info['name'],
                                                                   blue_info['ticker'],
                                                                   blue_info['members']['current'], True, blue_alliance)

        # Update all allinace info's
        for all_alliance_info in EveManager.get_all_alliance_info():
            all_alliance_api_info = EveApiManager.get_alliance_information(all_alliance_info.alliance_id)
            if 'alliance' in corp_standings:
                if int(all_alliance_info.alliance_id) in corp_standings['alliance']:
                    if int(corp_standings['alliance'][int(all_alliance_info.alliance_id)][
                        'standing']) >= settings.BLUE_STANDING:
                        EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                        all_alliance_api_info['executor_id'],
                                                        all_alliance_api_info['member_count'], True)
                    else:
                        EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                        all_alliance_api_info['executor_id'],
                                                        all_alliance_api_info['member_count'], False)
                else:
                    EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                    all_alliance_api_info['executor_id'],
                                                    all_alliance_api_info['member_count'], False)
            else:
                EveManager.update_alliance_info(all_alliance_api_info['id'],
                                                all_alliance_api_info['executor_id'],
                                                all_alliance_api_info['member_count'], False)

        # Update corp infos
        for all_corp_info in EveManager.get_all_corporation_info():
            alliance = None
            corpinfo = EveApiManager.get_corporation_information(all_corp_info.corporation_id)
            if corpinfo['alliance']['id'] is not None:
                alliance = EveManager.get_alliance_info_by_id(corpinfo['alliance']['id'])

            if alliance is not None and all_corp_info.alliance is not None:

                if int(alliance.alliance_id) in corp_standings['alliance']:
                    if int(corp_standings['alliance'][int(alliance.alliance_id)][
                        'standing']) >= settings.BLUE_STANDING:
                        EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance,
                                                           True)
                    else:
                        EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance,
                                                           False)
                else:
                    EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], alliance,
                                                       False)
            else:
                if int(all_corp_info.corporation_id) in corp_standings['alliance']:
                    if int(corp_standings['alliance'][int(all_corp_info.corporation_id)][
                        'standing']) >= settings.BLUE_STANDING:
                        EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], None, True)
                    else:
                        EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], None, False)
                else:
                    EveManager.update_corporation_info(corpinfo['id'], corpinfo['members']['current'], None, False)

        # Nuke the none believers
        # Check the corps
        for all_corp_info in EveManager.get_all_corporation_info():
            if all_corp_info.corporation_id != settings.CORP_ID:
                if not all_corp_info.is_blue:
                    all_corp_info.delete()

        # Check the alliances
        for all_alliance_info in EveManager.get_all_alliance_info():
            if all_alliance_info.is_blue is not True:
                all_alliance_info.delete()


