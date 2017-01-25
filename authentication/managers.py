from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.conf import settings
from authentication.states import NONE_STATE, BLUE_STATE, MEMBER_STATE
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
            authserviceinfo = AuthServicesInfo.objects.get(user=user)
            authserviceinfo.main_char_id = char_id
            authserviceinfo.save(update_fields=['main_char_id'])
            logger.info("Updated user %s main character to id %s" % (user, char_id))
        else:
            logger.error("Failed to update user %s main character id to %s: user does not exist." % (user, char_id))

    @staticmethod
    def update_is_blue(is_blue, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s blue status: %s" % (user, is_blue))
            authserviceinfo = AuthServicesInfo.objects.get(user=user)
            authserviceinfo.is_blue = is_blue
            authserviceinfo.save(update_fields=['is_blue'])
            logger.info("Updated user %s blue status to %s in authservicesinfo model." % (user, is_blue))


class UserState:
    def __init__(self):
        pass

    MEMBER_STATE = MEMBER_STATE
    BLUE_STATE = BLUE_STATE
    NONE_STATE = NONE_STATE

    @classmethod
    def member_state(cls, user):
        return cls.state_required(user, [cls.MEMBER_STATE])

    @classmethod
    def member_or_blue_state(cls, user):
        return cls.state_required(user, [cls.MEMBER_STATE, cls.BLUE_STATE])

    @classmethod
    def blue_state(cls, user):
        return cls.state_required(user, [cls.BLUE_STATE])

    @classmethod
    def none_state(cls, user):
        return cls.state_required(user, [cls.NONE_STATE])

    @classmethod
    def get_membership_state(cls, request):
        if request.user.is_authenticated:
            auth = AuthServicesInfo.objects.get(user=request.user)
            return {'STATE': auth.state}
        return {'STATE': cls.NONE_STATE}

    @staticmethod
    def state_required(user, states):
        if user.is_superuser and settings.SUPERUSER_STATE_BYPASS:
            return True
        if user.is_authenticated:
            auth = AuthServicesInfo.objects.get(user=user)
            return auth.state in states
        return False
