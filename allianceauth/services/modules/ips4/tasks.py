from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.services.hooks import NameFormatter
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
        logging.debug("Deleting all IPS4 users")
        Ips4User.objects.all().delete()

    @staticmethod
    def get_username(user):
        from .auth_hooks import Ips4Service
        return NameFormatter(Ips4Service(), user).format_name()
