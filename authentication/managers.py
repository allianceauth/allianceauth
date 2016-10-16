from __future__ import unicode_literals
from django.contrib.auth.models import User

from authentication.models import AuthServicesInfo

import logging

logger = logging.getLogger(__name__)


class AuthServicesInfoManager:
    def __init__(self):
        pass

    @staticmethod
    def update_main_char_id(char_id, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s main character to id %s" % (user, char_id))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.main_char_id = char_id
            authserviceinfo.save(update_fields=['main_char_id'])
            logger.info("Updated user %s main character to id %s" % (user, char_id))
        else:
            logger.error("Failed to update user %s main character id to %s: user does not exist." % (user, char_id))

    @staticmethod
    def update_user_forum_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s forum info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.forum_username = username
            authserviceinfo.save(update_fields=['forum_username'])
            logger.info("Updated user %s forum info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s forum info: user does not exist." % user)

    @staticmethod
    def update_user_jabber_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s jabber info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.jabber_username = username
            authserviceinfo.save(update_fields=['jabber_username'])
            logger.info("Updated user %s jabber info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s jabber info: user does not exist." % user)

    @staticmethod
    def update_user_mumble_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s mumble info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.mumble_username = username
            authserviceinfo.save(update_fields=['mumble_username'])
            logger.info("Updated user %s mumble info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s mumble info: user does not exist." % user)

    @staticmethod
    def update_user_ipboard_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s ipboard info: uername %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.ipboard_username = username
            authserviceinfo.save(update_fields=['ipboard_username'])
            logger.info("Updated user %s ipboard info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s ipboard info: user does not exist." % user)

    @staticmethod
    def update_user_xenforo_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s xenforo info: uername %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.xenforo_username = username
            authserviceinfo.save(update_fields=['xenforo_username'])
            logger.info("Updated user %s xenforo info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s xenforo info: user does not exist." % user)

    @staticmethod
    def update_user_teamspeak3_info(uid, perm_key, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s teamspeak3 info: uid %s" % (user, uid))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.teamspeak3_uid = uid
            authserviceinfo.teamspeak3_perm_key = perm_key
            authserviceinfo.save(update_fields=['teamspeak3_uid', 'teamspeak3_perm_key'])
            logger.info("Updated user %s teamspeak3 info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s teamspeak3 info: user does not exist." % user)

    @staticmethod
    def update_is_blue(is_blue, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s blue status: %s" % (user, is_blue))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.is_blue = is_blue
            authserviceinfo.save(update_fields=['is_blue'])
            logger.info("Updated user %s blue status to %s in authservicesinfo model." % (user, is_blue))

    @staticmethod
    def update_user_discord_info(user_id, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s discord info: user_id %s" % (user, user_id))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.discord_uid = user_id
            authserviceinfo.save(update_fields=['discord_uid'])
            logger.info("Updated user %s discord info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s discord info: user does not exist." % user)

    @staticmethod
    def update_user_discourse_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s discourse info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.discourse_username = username
            authserviceinfo.save(update_fields=['discourse_username'])
            logger.info("Updated user %s discourse info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s discourse info: user does not exist." % user)

    @staticmethod
    def update_user_ips4_info(username, id, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s IPS4 info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.ips4_username = username
            authserviceinfo.ips4_id = id
            authserviceinfo.save(update_fields=['ips4_username', 'ips4_id'])
            logger.info("Updated user %s IPS4 info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s IPS4 info: user does not exist." % user)

    @staticmethod
    def update_user_smf_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s forum info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.smf_username = username
            authserviceinfo.save(update_fields=['smf_username'])
            logger.info("Updated user %s smf info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s smf info: user does not exist." % user)

    @staticmethod
    def update_user_market_info(username, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s market info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.market_username = username
            authserviceinfo.save(update_fields=['market_username'])
            logger.info("Updated user %s market info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s market info: user does not exist." % user)
