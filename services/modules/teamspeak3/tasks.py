from __future__ import unicode_literals

import logging

from alliance_auth.celeryapp import app
from celery.schedules import crontab
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from notifications import notify

from authentication.models import AuthServicesInfo
from .util.ts3 import TeamspeakError
from .manager import Teamspeak3Manager
from .models import AuthTS, TSgroup, UserTSgroup, Teamspeak3User

logger = logging.getLogger(__name__)


class Teamspeak3Tasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            logger.debug("User %s has TS3 account %s. Deleting." % (user, user.teamspeak3.uid))
            if Teamspeak3Manager.delete_user(user.teamspeak3.uid):
                user.teamspeak3.delete()
                if notify_user:
                    notify(user, 'TeamSpeak3 Account Disabled', level='danger')
                return True
        return False

    @staticmethod
    def has_account(user):
        try:
            return user.teamspeak3.uid != ''
        except ObjectDoesNotExist:
            return False

    @staticmethod
    @app.task()
    def run_ts3_group_update():
        logger.debug("TS3 installed. Syncing local group objects.")
        Teamspeak3Manager._sync_ts_group_db()

    @staticmethod
    def disable():
        logger.info("Deleting all Teamspeak3Users")
        Teamspeak3User.objects.all().delete()
        logger.info("Deleting all UserTSgroup models")
        UserTSgroup.objects.all().delete()
        logger.info("Deleting all AuthTS models")
        AuthTS.objects.all().delete()
        logger.info("Deleting all TSgroup models")
        TSgroup.objects.all().delete()
        logger.info("Teamspeak3 disabled")

    @staticmethod
    @app.task(bind=True, name="teamspeak3.update_groups")
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating user %s teamspeak3 groups" % user)
        if Teamspeak3Tasks.has_account(user):
            usergroups = user.groups.all()
            groups = {}
            for usergroup in usergroups:
                filtered_groups = AuthTS.objects.filter(auth_group=usergroup)
                if filtered_groups:
                    for filtered_group in filtered_groups:
                        for ts_group in filtered_group.ts_group.all():
                            groups[ts_group.ts_group_name] = ts_group.ts_group_id
            logger.debug("Updating user %s teamspeak3 groups to %s" % (user, groups))
            try:
                Teamspeak3Manager.update_groups(user.teamspeak3.uid, groups)
                logger.debug("Updated user %s teamspeak3 groups." % user)
            except TeamspeakError as e:
                logger.error("Error occured while syncing TS groups for %s: %s" % (user, str(e)))
                raise self.retry(countdown=60*10)
        else:
            logger.debug("User does not have a teamspeak3 account")

    @staticmethod
    @app.task(name="teamspeak3.update_all_groups")
    def update_all_groups():
        logger.debug("Updating ALL teamspeak3 groups")
        for user in Teamspeak3User.objects.exclude(uid__exact=''):
            Teamspeak3Tasks.update_groups.delay(user.user_id)
