from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from notifications import notify

from .models import MarketUser
from .manager import MarketManager


import logging

logger = logging.getLogger(__name__)


class MarketTasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            logger.debug("User %s has a Market account %s. Deleting." % (user, user.market.username))
            if MarketManager.disable_user(user.market.username):
                user.market.delete()
                if notify_user:
                    notify(user, 'Alliance Market Account Disabled', level='danger')
                return True
        return False

    @staticmethod
    def has_account(user):
        try:
            return user.market.username != ''
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def disable():
        if settings.ENABLE_AUTH_MARKET:
            logger.warn("ENABLE_AUTH_MARKET still True, after disabling users will still be able to activate Market accounts")
        if settings.ENABLE_BLUE_MARKET:
            logger.warn("ENABLE_BLUE_MARKET still True, after disabling blues will still be able to activate Market accounts")
        MarketUser.objects.all().delete()
