from authentication.models import AuthServicesInfo
from celerytask.models import SyncGroupCache
from django.conf import settings
import logging
from services.models import UserTSgroup
from services.models import AuthTS
from services.models import TSgroup
from services.models import DiscordAuthToken

logger = logging.getLogger(__name__)

def disable_teamspeak():
    if settings.ENABLE_AUTH_TEAMSPEAK3:
        logger.warn("ENABLE_AUTH_TEAMSPEAK3 still True, after disabling users will still be able to create teamspeak accounts")
    if settings.ENABLE_BLUE_TEAMSPEAK3:
        logger.warn("ENABLE_BLUE_TEAMSPEAK3 still True, after disabling blues will still be able to create teamspeak accounts")
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
        if auth.forum_password:
            logger.info("Clearing %s forum password" % auth.user)
            auth.forum_password = ''
            auth.save()
    logger.info("Deleting all SyncGroupCache models for forum")
    SyncGroupCache.objects.filter(servicename="forum").delete()

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
        if auth.jabber_password:
            logger.info("Clearing %s jabber password" % auth.user)
            auth.jabber_password = ''
            auth.save()
    logger.info("Deleting all SyncGroupCache models for jabber")
    SyncGroupCache.objects.filter(servicename="jabber").delete()

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
        if auth.mumble_password:
            logger.info("Clearing %s mumble password" % auth.user)
            auth.mumble_password = ''
            auth.save()
    logger.info("Deleting all SyncGroupCache models for mumble")
    SyncGroupCache.objects.filter(servicename="mumble").delete()

def disable_ipboard():
    if settings.ENABLE_AUTH_IPBOARD:
        logger.warn("ENABLE_AUTH_IPBOARD still True, after disabling users will still be able to create IPBoard accounts")
    if settings.ENABLE_BLUE_IPBOARD:
        logger.warn("ENABLE_BLUE_IPBOARD still True, after disabling blues will still be able to create IPBoard accounts")
    for auth in AuthServicesInfo.objects.all():
        if auth.ipboard_username:
            logger.info("Clearing %s ipboard username" % auth.user)
            auth.ipboard_username = ''
            auth.save()
        if auth.ipboard_password:
            logger.info("Clearing %s ipboard password" % auth.user)
            auth.ipboard_password = ''
            auth.save()
    logger.info("Deleting all SyncGroupCache models for ipboard")
    SyncGroupCache.objects.filter(servicename="ipboard").delete()


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
    logger.info("Deleting all DiscordAuthToken models")
    DiscordAuthToken.objects.all().delete()
