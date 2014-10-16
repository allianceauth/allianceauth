from models import SyncGroupCache
from django.conf import settings
from celery.task import periodic_task
from celery.task.schedules import crontab
from django.contrib.auth.models import User
from services.managers.jabber_manager import JabberManager
from services.managers.mumble_manager import MumbleManager
from services.managers.forum_manager import ForumManager
from authentication.models import AuthServicesInfo
from eveonline.managers import EveManager
from services.managers.eve_api_manager import EveApiManager
from util.common_task import deactivate_services

def update_jabber_groups(user):
    syncgroups = SyncGroupCache.objects.filter(user=user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for syncgroup in syncgroups:
        groups.append(str(syncgroup.groupname))

    if len(groups) == 0:
        groups.append('empty')

    JabberManager.update_user_groups(authserviceinfo.jabber_username, authserviceinfo.jabber_password, groups)


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

    ForumManager.update_groups(authserviceinfo.forum_username, groups)


def add_to_databases(user, groups, syncgroups):

    authserviceinfo = None
    try:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)
    except:
        pass

    if authserviceinfo:
        authserviceinfo = AuthServicesInfo.objects.get(user=user)

        update = False
        for group in groups:
            syncgroup = syncgroups.filter(groupname=group.name)
            if not syncgroup:
                # gotta create group
                # create syncgroup
                # create service groups
                synccache = SyncGroupCache()
                synccache.groupname = group.name
                synccache.user = user
                synccache.save()
                update = True

        if update:
            if authserviceinfo.jabber_username != "":
                update_jabber_groups(user)
            if authserviceinfo.mumble_username != "":
                update_mumble_groups(user)
            if authserviceinfo.forum_username != "":
                update_forum_groups(user)


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
            if authserviceinfo.jabber_username != "":
                update_jabber_groups(user)
            if authserviceinfo.mumble_username != "":
                update_mumble_groups(user)
            if authserviceinfo.forum_username != "":
                update_forum_groups(user)


#run every minute
@periodic_task(run_every=crontab(minute="*/1"))
def run_databaseUpdate():
    users = User.objects.all()
    for user in users:
        groups = user.groups.all()
        syncgroups = SyncGroupCache.objects.filter(user=user)
        add_to_databases(user, groups, syncgroups)
        remove_from_databases(user, groups, syncgroups)


#run at midnight everyday
@periodic_task(run_every=crontab(minute=0, hour="*/3"))
def run_api_refresh():
    users = User.objects.all()
    for user in users:
        api_key_pairs = EveManager.get_api_key_pairs(user.id)
        if api_key_pairs:
            valid_key = False
            authserviceinfo = AuthServicesInfo.objects.get(user=user)
            # We do a check on the authservice info to insure that we shoud run the check
            # No point in running the check on people who arn't on services
            print 'Running update on user: '+user.username
            if authserviceinfo.main_char_id:
                if authserviceinfo.main_char_id != "":
                    for api_key_pair in api_key_pairs:
                        print 'Running on '+api_key_pair.api_id+':'+api_key_pair.api_key
                        if EveApiManager.api_key_is_valid(api_key_pair.api_id, api_key_pair.api_key):
                            # Update characters
                            characters = EveApiManager.get_characters_from_api(api_key_pair.api_id, api_key_pair.api_key)
                            EveManager.update_characters_from_list(characters)
                            valid_key = True
                        else:
                            EveManager.delete_characters_by_api_id(api_key_pair.api_id, api_key_pair.api_key)
                            EveManager.delete_api_key_pair(api_key_pair.api_id, api_key_pair.api_key)

                    if valid_key:
                        # Check our main character
                        main_alliance_id = EveManager.get_charater_alliance_id_by_id(authserviceinfo.main_char_id)
                        if main_alliance_id == settings.ALLIANCE_ID:
                            pass
                        else:
                            deactivate_services(user)
                    else:
                        #nuke it
                        deactivate_services(user)
            else:
                print 'No main_char_id set'