from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .manager import Ips4Manager
from .models import Ips4User

import logging

logger = logging.getLogger(__name__)


class Ips4Tasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user):
        logging.debug("Attempting to delete IPS4 account for %s" % user)
        if cls.has_account(user) and Ips4Manager.delete_user(user.ips4.id):
            user.ips4.delete()
            logger.info("Successfully deactivated IPS4 for user %s" % user)
            return True
        return False

    @staticmethod
    def has_account(user):
        try:
            return user.ips4.id != ''
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def disable():
        if settings.ENABLE_AUTH_IPS4:
            logger.warn(
                "ENABLE_AUTH_IPS4 still True, after disabling users will still be able to create IPS4 accounts")
        if settings.ENABLE_BLUE_IPS4:
            logger.warn(
                "ENABLE_BLUE_IPS4 still True, after disabling blues will still be able to create IPS4 accounts")
        logging.debug("Deleting all IPS4 users")
        Ips4User.objects.all().delete()
