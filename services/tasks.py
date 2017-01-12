from __future__ import unicode_literals
from django.conf import settings
import logging
from django.contrib.auth.models import User
from celery import task
from services.models import UserTSgroup
from services.models import AuthTS
from services.models import TSgroup
from services.models import MumbleUser
from authentication.managers import AuthServicesInfoManager
from authentication.models import AuthServicesInfo
from services.managers.openfire_manager import OpenfireManager
from services.managers.phpbb3_manager import Phpbb3Manager
from services.managers.mumble_manager import MumbleManager
from services.managers.ipboard_manager import IPBoardManager
from services.managers.teamspeak3_manager import Teamspeak3Manager
from services.managers.discord_manager import DiscordOAuthManager
from services.managers.xenforo_manager import XenForoManager
from services.managers.market_manager import marketManager
from services.managers.discourse_manager import DiscourseManager
from services.managers.smf_manager import smfManager
from services.managers.util.ts3 import TeamspeakError
from authentication.states import MEMBER_STATE, BLUE_STATE
from notifications import notify
from celery.task import periodic_task
from celery.task.schedules import crontab
from eveonline.managers import EveManager
import redis

REDIS_CLIENT = redis.Redis()

logger = logging.getLogger(__name__)

# http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
def only_one(function=None, key="", timeout=None):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""

        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec


@periodic_task(run_every=crontab(minute="*/30"))
def run_ts3_group_update():
    if settings.ENABLE_AUTH_TEAMSPEAK3 or settings.ENABLE_BLUE_TEAMSPEAK3:
        logger.debug("TS3 installed. Syncing local group objects.")
        Teamspeak3Manager._sync_ts_group_db()


def disable_teamspeak():
    if settings.ENABLE_AUTH_TEAMSPEAK3:
        logger.warn(
            "ENABLE_AUTH_TEAMSPEAK3 still True, after disabling users will still be able to create teamspeak accounts")
    if settings.ENABLE_BLUE_TEAMSPEAK3:
        logger.warn(
            "ENABLE_BLUE_TEAMSPEAK3 still True, after disabling blues will still be able to create teamspeak accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.teamspeak3_uid:
            logger.info("Clearing %s Teamspeak3 UID" % auth.user)
            auth.teamspeak3_uid = ''
            auth.save()
        if auth.teamspeak3_perm_key:
            logger.info("Clearing %s Teamspeak3 permission key" % auth.user)
            auth.teamspeak3_perm_key = ''
            auth.save()
    logger.info("Deleting all UserTSgroup models")
    UserTSgroup.objects.all().delete()
    logger.info("Deleting all AuthTS models")
    AuthTS.objects.all().delete()
    logger.info("Deleting all TSgroup models")
    TSgroup.objects.all().delete()
    logger.info("Teamspeak3 disabled")


def disable_forum():
    if settings.ENABLE_AUTH_FORUM:
        logger.warn("ENABLE_AUTH_FORUM still True, after disabling users will still be able to create forum accounts")
    if settings.ENABLE_BLUE_FORUM:
        logger.warn("ENABLE_BLUE_FORUM still True, after disabling blues will still be able to create forum accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.forum_username:
            logger.info("Clearing %s forum username" % auth.user)
            auth.forum_username = ''
            auth.save()


def disable_jabber():
    if settings.ENABLE_AUTH_JABBER:
        logger.warn("ENABLE_AUTH_JABBER still True, after disabling users will still be able to create jabber accounts")
    if settings.ENABLE_BLUE_JABBER:
        logger.warn("ENABLE_BLUE_JABBER still True, after disabling blues will still be able to create jabber accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.jabber_username:
            logger.info("Clearing %s jabber username" % auth.user)
            auth.jabber_username = ''
            auth.save()


def disable_mumble():
    if settings.ENABLE_AUTH_MUMBLE:
        logger.warn("ENABLE_AUTH_MUMBLE still True, after disabling users will still be able to create mumble accounts")
    if settings.ENABLE_BLUE_MUMBLE:
        logger.warn("ENABLE_BLUE_MUMBLE still True, after disabling blues will still be able to create mumble accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.mumble_username:
            logger.info("Clearing %s mumble username" % auth.user)
            auth.mumble_username = ''
            auth.save()
    logger.info("Deleting all MumbleUser models")
    MumbleUser.objects.all().delete()


def disable_ipboard():
    if settings.ENABLE_AUTH_IPBOARD:
        logger.warn(
            "ENABLE_AUTH_IPBOARD still True, after disabling users will still be able to create IPBoard accounts")
    if settings.ENABLE_BLUE_IPBOARD:
        logger.warn(
            "ENABLE_BLUE_IPBOARD still True, after disabling blues will still be able to create IPBoard accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.ipboard_username:
            logger.info("Clearing %s ipboard username" % auth.user)
            auth.ipboard_username = ''
            auth.save()


def disable_discord():
    if settings.ENABLE_AUTH_DISCORD:
        logger.warn("ENABLE_AUTH_DISCORD still True, after disabling users will still be able to link Discord accounts")
    if settings.ENABLE_BLUE_DISCORD:
        logger.warn("ENABLE_BLUE_DISCORD still True, after disabling blues will still be able to link Discord accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.discord_uid:
            logger.info("Clearing %s Discord UID" % auth.user)
            auth.discord_uid = ''
            auth.save()


def disable_market():
    if settings.ENABLE_AUTH_MARKET:
        logger.warn("ENABLE_AUTH_MARKET still True, after disabling users will still be able to activate Market accounts")
    if settings.ENABLE_BLUE_DISCORD:
        logger.warn("ENABLE_BLUE_MARKET still True, after disabling blues will still be able to activate Market accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.market_username:
            logger.info("Clearing %s market username" % auth.user)
            auth.market_username = ''
            auth.save()


def deactivate_services(user):
    change = False
    logger.debug("Deactivating services for user %s" % user)
    authinfo = AuthServicesInfo.objects.get(user=user)
    if authinfo.mumble_username and authinfo.mumble_username != "":
        logger.debug("User %s has mumble account %s. Deleting." % (user, authinfo.mumble_username))
        MumbleManager.delete_user(authinfo.mumble_username)
        AuthServicesInfoManager.update_user_mumble_info("", user)
        change = True
    if authinfo.jabber_username and authinfo.jabber_username != "":
        logger.debug("User %s has jabber account %s. Deleting." % (user, authinfo.jabber_username))
        OpenfireManager.delete_user(authinfo.jabber_username)
        AuthServicesInfoManager.update_user_jabber_info("", user)
        change = True
    if authinfo.forum_username and authinfo.forum_username != "":
        logger.debug("User %s has forum account %s. Deleting." % (user, authinfo.forum_username))
        Phpbb3Manager.disable_user(authinfo.forum_username)
        AuthServicesInfoManager.update_user_forum_info("", user)
        change = True
    if authinfo.ipboard_username and authinfo.ipboard_username != "":
        logger.debug("User %s has ipboard account %s. Deleting." % (user, authinfo.ipboard_username))
        IPBoardManager.disable_user(authinfo.ipboard_username)
        AuthServicesInfoManager.update_user_ipboard_info("", user)
        change = True
    if authinfo.teamspeak3_uid and authinfo.teamspeak3_uid != "":
        logger.debug("User %s has mumble account %s. Deleting." % (user, authinfo.teamspeak3_uid))
        Teamspeak3Manager.delete_user(authinfo.teamspeak3_uid)
        AuthServicesInfoManager.update_user_teamspeak3_info("", "", user)
        change = True
    if authinfo.discord_uid and authinfo.discord_uid != "":
        logger.debug("User %s has discord account %s. Deleting." % (user, authinfo.discord_uid))
        DiscordOAuthManager.delete_user(authinfo.discord_uid)
        AuthServicesInfoManager.update_user_discord_info("", user)
        change = True
    if authinfo.xenforo_username and authinfo.xenforo_password != "":
        logger.debug("User %s has a XenForo account %s. Deleting." % (user, authinfo.xenforo_username))
        XenForoManager.disable_user(authinfo.xenforo_username)
        AuthServicesInfoManager.update_user_xenforo_info("", user)
        change = True
    if authinfo.market_username and authinfo.market_username != "":
        logger.debug("User %s has a Market account %s. Deleting." % (user, authinfo.market_username))
        marketManager.disable_user(authinfo.market_username)
        AuthServicesInfoManager.update_user_market_info("", user)
        change = True
    if authinfo.discourse_enabled:
        logger.debug("User %s has a Discourse account. Disabling login." % user)
        DiscourseManager.disable_user(user)
        authinfo.discourse_enabled = False
        authinfo.save()
        change = True
    if authinfo.smf_username and authinfo.smf_username != "":
        logger.debug("User %s has a SMF account %s. Deleting." % (user, authinfo.smf_username))
        smfManager.disable_user(authinfo.smf_username)
        AuthServicesInfoManager.update_user_smf_info("", user)
        change = True
    if change:
        notify(user, "Services Disabled", message="Your services accounts have been disabled.", level="danger")


@task(bind=True)
def validate_services(self, user, state):
    if state == MEMBER_STATE:
        setting_string = 'AUTH'
    elif state == BLUE_STATE:
        setting_string = 'BLUE'
    else:
        deactivate_services(user)
        return
    logger.debug('Ensuring user %s services are available to state %s' % (user, state))
    auth = AuthServicesInfo.objects.get(user=user)
    if auth.mumble_username and not getattr(settings, 'ENABLE_%s_MUMBLE' % setting_string, False):
        MumbleManager.delete_user(auth.mumble_username)
        AuthServicesInfoManager.update_user_mumble_info("", user)
        notify(user, 'Mumble Account Disabled', level='danger')
    if auth.jabber_username and not getattr(settings, 'ENABLE_%s_JABBER' % setting_string, False):
        OpenfireManager.delete_user(auth.jabber_username)
        AuthServicesInfoManager.update_user_jabber_info("", user)
        notify(user, 'Jabber Account Disabled', level='danger')
    if auth.forum_username and not getattr(settings, 'ENABLE_%s_FORUM' % setting_string, False):
        Phpbb3Manager.disable_user(auth.forum_username)
        AuthServicesInfoManager.update_user_forum_info("", user)
        notify(user, 'Forum Account Disabled', level='danger')
    if auth.ipboard_username and not getattr(settings, 'ENABLE_%s_IPBOARD' % setting_string, False):
        IPBoardManager.disable_user(auth.ipboard_username)
        AuthServicesInfoManager.update_user_ipboard_info("", user)
        notify(user, 'IPBoard Account Disabled', level='danger')
    if auth.teamspeak3_uid and not getattr(settings, 'ENABLE_%s_TEAMSPEAK' % setting_string, False):
        Teamspeak3Manager.delete_user(auth.teamspeak3_uid)
        AuthServicesInfoManager.update_user_teamspeak3_info("", "", user)
        notify(user, 'TeamSpeak3 Account Disabled', level='danger')
    if auth.discord_uid and not getattr(settings, 'ENABLE_%s_DISCORD' % setting_string, False):
        DiscordOAuthManager.delete_user(auth.discord_uid)
        AuthServicesInfoManager.update_user_discord_info("", user)
        notify(user, 'Discord Account Disabled', level='danger')
    if auth.xenforo_username and not getattr(settings, 'ENABLE_%s_XENFORO' % setting_string, False):
        XenForoManager.disable_user(auth.xenforo_username)
        AuthServicesInfoManager.update_user_xenforo_info("", user)
        notify(user, 'XenForo Account Disabled', level='danger')
    if auth.market_username and not getattr(settings, 'ENABLE_%s_MARKET' % setting_string, False):
        marketManager.disable_user(auth.market_username)
        AuthServicesInfoManager.update_user_market_info("", user)
        notify(user, 'Alliance Market Account Disabled', level='danger')
    if auth.discourse_enabled and not getattr(settings, 'ENABLE_%s_DISCOURSE' % setting_string, False):
        DiscourseManager.disable_user(user)
        authinfo.discourse_enabled = False
        authinfo.save()
        notify(user, 'Discourse Account Disabled', level='danger')
    if auth.smf_username and not getattr(settings, 'ENABLE_%s_SMF' % setting_string, False):
        smfManager.disable_user(auth.smf_username)
        AuthServicesInfoManager.update_user_smf_info(auth.smf_username, user)
        notify(user, "SMF Account Disabled", level='danger')


@task(bind=True)
def update_jabber_groups(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating jabber groups for user %s" % user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s jabber groups to %s" % (user, groups))
    try:
        OpenfireManager.update_user_groups(authserviceinfo.jabber_username, groups)
    except:
        logger.exception("Jabber group sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s jabber groups." % user)


@task
def update_all_jabber_groups():
    logger.debug("Updating ALL jabber groups")
    for user in AuthServicesInfo.objects.exclude(jabber_username__exact=''):
        update_jabber_groups.delay(user.user_id)


@task(bind=True)
def update_mumble_groups(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating mumble groups for user %s" % user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s mumble groups to %s" % (user, groups))
    try:
        MumbleManager.update_groups(authserviceinfo.mumble_username, groups)
    except:
        logger.exception("Mumble group sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s mumble groups." % user)


@task
def update_all_mumble_groups():
    logger.debug("Updating ALL mumble groups")
    for user in AuthServicesInfo.objects.exclude(mumble_username__exact=''):
        update_mumble_groups.delay(user.user_id)


@task(bind=True)
def update_forum_groups(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating forum groups for user %s" % user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s forum groups to %s" % (user, groups))
    try:
        Phpbb3Manager.update_groups(authserviceinfo.forum_username, groups)
    except:
        logger.exception("Phpbb group sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s forum groups." % user)


@task
def update_all_forum_groups():
    logger.debug("Updating ALL forum groups")
    for user in AuthServicesInfo.objects.exclude(forum_username__exact=''):
        update_forum_groups.delay(user.user_id)


@task(bind=True)
def update_smf_groups(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating smf groups for user %s" % user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s smf groups to %s" % (user, groups))
    try:
        smfManager.update_groups(authserviceinfo.smf_username, groups)
    except:
        logger.exception("smf group sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s smf groups." % user)


@task
def update_all_smf_groups():
    logger.debug("Updating ALL smf groups")
    for user in AuthServicesInfo.objects.exclude(smf_username__exact=''):
        update_smf_groups.delay(user.user_id)


@task(bind=True)
def update_ipboard_groups(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating user %s ipboard groups." % user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    if len(groups) == 0:
        groups.append('empty')
    logger.debug("Updating user %s ipboard groups to %s" % (user, groups))
    try:
        IPBoardManager.update_groups(authserviceinfo.ipboard_username, groups)
    except:
        logger.exception("IPBoard group sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s ipboard groups." % user)


@task
def update_all_ipboard_groups():
    logger.debug("Updating ALL ipboard groups")
    for user in AuthServicesInfo.objects.exclude(ipboard_username__exact=''):
        update_ipboard_groups.delay(user.user_id)


@task(bind=True)
def update_teamspeak3_groups(self, pk):
    user = User.objects.get(pk=pk)
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
    try:
        Teamspeak3Manager.update_groups(authserviceinfo.teamspeak3_uid, groups)
        logger.debug("Updated user %s teamspeak3 groups." % user)
    except TeamspeakError as e:
        logger.error("Error occured while syncing TS groups for %s: %s" % (user, str(e)))
        raise self.retry(countdown=60*10)


@task
def update_all_teamspeak3_groups():
    logger.debug("Updating ALL teamspeak3 groups")
    for user in AuthServicesInfo.objects.exclude(teamspeak3_uid__exact=''):
        update_teamspeak3_groups.delay(user.user_id)


@task(bind=True)
@only_one(key="Discord", timeout=60*5)
def update_discord_groups(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating discord groups for user %s" % user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    if len(groups) == 0:
        logger.debug("No syncgroups found for user. Adding empty group.")
        groups.append('empty')
    logger.debug("Updating user %s discord groups to %s" % (user, groups))
    try:
        DiscordOAuthManager.update_groups(authserviceinfo.discord_uid, groups)
    except:
        logger.exception("Discord group sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s discord groups." % user)


@task
def update_all_discord_groups():
    logger.debug("Updating ALL discord groups")
    for user in AuthServicesInfo.objects.exclude(discord_uid__exact=''):
        update_discord_groups.delay(user.user_id)


@task(bind=True)
def update_discord_nickname(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating discord nickname for user %s" % user)
    authserviceinfo = AuthServicesInfo.objects.get(user=user)
    character = EveManager.get_character_by_id(authserviceinfo.main_char_id)
    logger.debug("Updating user %s discord nickname to %s" % (user, character.character_name))
    try:
        DiscordOAuthManager.update_nickname(authserviceinfo.discord_uid, character.character_name)
    except:
        logger.exception("Discord nickname sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s discord nickname." % user)


@task
def update_all_discord_nicknames():
    logger.debug("Updating ALL discord nicknames")
    for user in AuthServicesInfo.objects.exclude(discord_uid__exact=''):
        update_discord_nickname(user.user_id)


@task(bind=True)
def update_discourse_groups(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug("Updating discourse groups for user %s" % user)
    try:
        DiscourseManager.update_groups(user)
    except:
        logger.warn("Discourse group sync failed for %s, retrying in 10 mins" % user)
        raise self.retry(countdown=60 * 10)
    logger.debug("Updated user %s discourse groups." % user)


@task
def update_all_discourse_groups():
    logger.debug("Updating ALL discourse groups")
    for user in AuthServicesInfo.objects.filter(discourse_enabled=True):
        update_discourse_groups.delay(user.pk)
