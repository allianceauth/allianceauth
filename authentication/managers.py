from django.contrib.auth.models import User

from models import AuthServicesInfo

import logging

logger = logging.getLogger(__name__)

class AuthServicesInfoManager:
    def __init__(self):
        pass

    @staticmethod
    def __get_or_create(user):
        if AuthServicesInfo.objects.filter(user=user).exists():
            logger.debug("Returning existing authservicesinfo model for user %s" % user)
            return AuthServicesInfo.objects.get(user=user)
        else:
            # We have to create
            logger.info("Creating new authservicesinfo model for user %s" % user)
            authserviceinfo = AuthServicesInfo()
            authserviceinfo.user = user
            authserviceinfo.save()
            return authserviceinfo

    @staticmethod
    def get_auth_service_info(user):
        if User.objects.filter(username=user.username).exists():
            return AuthServicesInfoManager.__get_or_create(user)
        logger.error("Failed to get authservicesinfo object for user %s: user does not exist." % user)
        return None

    @staticmethod
    def update_main_char_Id(char_id, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s main character to id %s" % (user, char_id))
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.main_char_id = char_id
            authserviceinfo.save(update_fields=['main_char_id'])
            logger.info("Updated user %s main character to id %s" % (user, char_id))
        logger.error("Failed to update user %s main character id to %s: user does not exist." % (user, char_id))

    @staticmethod
    def update_user_forum_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s forum info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.forum_username = username
            authserviceinfo.forum_password = password
            authserviceinfo.save(update_fields=['forum_username', 'forum_password'])
            logger.info("Updated user %s forum info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s forum info: user does not exist." % user)

    @staticmethod
    def update_user_jabber_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s jabber info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.jabber_username = username
            authserviceinfo.jabber_password = password
            authserviceinfo.save(update_fields=['jabber_username', 'jabber_password'])
            logger.info("Updated user %s jabber info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s jabber info: user does not exist." % user)


    @staticmethod
    def update_user_mumble_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s mumble info: username %s" % (user, username))
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.mumble_username = username
            authserviceinfo.mumble_password = password
            authserviceinfo.save(update_fields=['mumble_username', 'mumble_password'])
            logger.info("Updated user %s mumble info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s mumble info: user does not exist." % user)

    @staticmethod
    def update_user_ipboard_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s ipboard info: uername %s" % (user, username))
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.ipboard_username = username
            authserviceinfo.ipboard_password = password
            authserviceinfo.save(update_fields=['ipboard_username', 'ipboard_password'])
            logger.info("Updated user %s ipboard info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s ipboard info: user does not exist." % user)

    @staticmethod
    def update_user_teamspeak3_info(uid, perm_key, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s teamspeak3 info: uid %s" % (user, uid))
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
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
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.is_blue = is_blue
            authserviceinfo.save(update_fields=['is_blue'])
            logger.info("Updated user %s blue status to %s in authservicesinfo model." % (user, is_blue))

    @staticmethod
    def update_user_discord_info(user_id, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s discord info: user_id %s" % (user, user_id))
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.discord_uid = user_id
            authserviceinfo.save(update_fields=['discord_uid'])
            logger.info("Updated user %s discord info in authservicesinfo model." % user)
        else:
            logger.error("Failed to update user %s discord info: user does not exist." % user)
