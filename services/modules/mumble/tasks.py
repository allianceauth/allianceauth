from __future__ import unicode_literals

from alliance_auth.celeryapp import app
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .models import MumbleUser
from .manager import MumbleManager

import logging

logger = logging.getLogger(__name__)


class MumbleTasks:
    def __init__(self):
        pass

    @staticmethod
    def has_account(user):
        try:
            return user.mumble.username != ''
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def disable_mumble():
        logger.info("Deleting all MumbleUser models")
        MumbleUser.objects.all().delete()

    @staticmethod
    @app.task(bind=True, name="mumble.update_groups")
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating mumble groups for user %s" % user)
        if MumbleTasks.has_account(user):
            groups = []
            for group in user.groups.all():
                groups.append(str(group.name))
            if len(groups) == 0:
                groups.append('empty')
            logger.debug("Updating user %s mumble groups to %s" % (user, groups))
            try:
                if not MumbleManager.update_groups(user, groups):
                    raise Exception("Group sync failed")
            except:
                logger.exception("Mumble group sync failed for %s, retrying in 10 mins" % user)
                raise self.retry(countdown=60 * 10)
            logger.debug("Updated user %s mumble groups." % user)
        else:
            logger.debug("User %s does not have a mumble account, skipping" % user)

    @staticmethod
    @app.task(name="mumble.update_all_groups")
    def update_all_groups():
        logger.debug("Updating ALL mumble groups")
        for mumble_user in MumbleUser.objects.exclude(username__exact=''):
            MumbleTasks.update_groups.delay(mumble_user.user.pk)
