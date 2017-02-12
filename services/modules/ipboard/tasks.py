from __future__ import unicode_literals

from alliance_auth.celeryapp import app
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from notifications import notify

from .manager import IPBoardManager
from .models import IpboardUser

import logging

logger = logging.getLogger(__name__)


class IpboardTasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            if IPBoardManager.disable_user(user.ipboard.username):
                user.ipboard.delete()
                if notify_user:
                    notify(user, 'IPBoard Account Disabled', level='danger')
                return True
        return False

    @staticmethod
    def has_account(user):
        try:
            return user.ipboard.username != ''
        except ObjectDoesNotExist:
            return False

    @staticmethod
    @app.task(bind=True, name='ipboard.update_groups')
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating user %s ipboard groups." % user)
        groups = []
        for group in user.groups.all():
            groups.append(str(group.name))
        if len(groups) == 0:
            groups.append('empty')
        logger.debug("Updating user %s ipboard groups to %s" % (user, groups))
        try:
            IPBoardManager.update_groups(user.ipboard.username, groups)
        except:
            logger.exception("IPBoard group sync failed for %s, retrying in 10 mins" % user)
            raise self.retry(countdown=60 * 10)
        logger.debug("Updated user %s ipboard groups." % user)

    @staticmethod
    @app.task(name='ipboard.update_all_groups')
    def update_all_groups():
        logger.debug("Updating ALL ipboard groups")
        for ipboard_user in IpboardUser.objects.exclude(username__exact=''):
            IpboardTasks.update_groups.delay(ipboard_user.user.pk)

    @staticmethod
    def disable():
        logger.debug("Deleting all Ipboard Users")
        IpboardUser.objects.all().delete()
