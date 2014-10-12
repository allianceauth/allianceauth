from models import SyncGroupCache
from celery import task
from celery.task import periodic_task
from celery.task.schedules import crontab
from django.contrib.auth.models import User
from services.managers.jabber_manager import JabberManager
from services.managers.mumble_manager import MumbleManager
from services.managers.forum_manager import ForumManager
from authentication.models import AuthServicesInfo
from django.utils.timezone import timedelta


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


@periodic_task(run_every=crontab(minute="*/1"))
def run_databaseUpdate():
    users = User.objects.all()
    for user in users:
        groups = user.groups.all()
        syncgroups = SyncGroupCache.objects.filter(user=user)
        add_to_databases(user, groups, syncgroups)
        remove_from_databases(user, groups, syncgroups)
