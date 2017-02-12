from __future__ import unicode_literals

import logging

from alliance_auth.celeryapp import app
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from notifications import notify

from .manager import SmfManager
from .models import SmfUser

logger = logging.getLogger(__name__)


class SmfTasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            logger.debug("User %s has a SMF account %s. Deleting." % (user, user.smf.username))
            SmfManager.disable_user(user.smf.username)
            user.smf.delete()
            if notify_user:
                notify(user, "SMF Account Disabled", level='danger')
            return True
        return False

    @staticmethod
    def has_account(user):
        try:
            return user.smf.username != ''
        except ObjectDoesNotExist:
            return False

    @classmethod
    def disable(cls):
        SmfUser.objects.all().delete()

    @staticmethod
    @app.task(bind=True, name="smf.update_groups")
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating smf groups for user %s" % user)
        if SmfTasks.has_account(user):
            groups = []
            for group in user.groups.all():
                groups.append(str(group.name))
            if len(groups) == 0:
                groups.append('empty')
            logger.debug("Updating user %s smf groups to %s" % (user, groups))
            try:
                SmfManager.update_groups(user.smf.username, groups)
            except:
                logger.exception("smf group sync failed for %s, retrying in 10 mins" % user)
                raise self.retry(countdown=60 * 10)
            logger.debug("Updated user %s smf groups." % user)
        else:
            logger.debug("User does not have an smf account")

    @staticmethod
    @app.task(name="smf.update_all_groups")
    def update_all_groups():
        logger.debug("Updating ALL smf groups")
        for user in SmfUser.objects.exclude(username__exact=''):
            SmfTasks.update_groups.delay(user.user_id)
