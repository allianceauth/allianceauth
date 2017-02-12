from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from notifications import notify

from .manager import XenForoManager
from .models import XenforoUser

import logging

logger = logging.getLogger(__name__)


class XenforoTasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            logger.debug("User %s has a XenForo account %s. Deleting." % (user, user.xenforo.username))
            if XenForoManager.disable_user(user.xenforo.username) == 200:
                user.xenforo.delete()
                if notify_user:
                    notify(user, 'XenForo Account Disabled', level='danger')
                return True
        return False

    @staticmethod
    def has_account(user):
        try:
            return user.xenforo.username != ''
        except ObjectDoesNotExist:
            return False

    @classmethod
    def disable(cls):
        logger.debug("Deleting ALL XenForo users")
        XenforoUser.objects.all().delete()
