import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from allianceauth.services.tasks import QueueOnce
from allianceauth.notifications import notify
from allianceauth.services.hooks import NameFormatter
from .manager import Teamspeak3Manager
from .models import AuthTS, TSgroup, UserTSgroup, Teamspeak3User
from .util.ts3 import TeamspeakError

logger = logging.getLogger(__name__)


class Teamspeak3Tasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            logger.debug("User %s has TS3 account %s. Deleting." % (user, user.teamspeak3.uid))
            with Teamspeak3Manager() as ts3man:
                if ts3man.delete_user(user.teamspeak3.uid):
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
    @shared_task
    def run_ts3_group_update():
        logger.debug("TS3 installed. Syncing local group objects.")
        with Teamspeak3Manager() as ts3man:
            ts3man._sync_ts_group_db()

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
    @shared_task(bind=True, name="teamspeak3.update_groups", base=QueueOnce)
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
            for stategroup in user.profile.state.stategroup_set.all():
                groups[stategroup.ts_group.ts_group_name] = stategroup.ts_group.ts_group_id
            logger.debug("Updating user %s teamspeak3 groups to %s" % (user, groups))
            try:
                with Teamspeak3Manager() as ts3man:
                    ts3man.update_groups(user.teamspeak3.uid, groups)
                logger.debug("Updated user %s teamspeak3 groups." % user)
            except TeamspeakError as e:
                logger.error("Error occured while syncing TS groups for %s: %s" % (user, str(e)))
                raise self.retry(countdown=60*10)
        else:
            logger.debug("User does not have a teamspeak3 account")

    @staticmethod
    @shared_task(name="teamspeak3.update_all_groups")
    def update_all_groups():
        logger.debug("Updating ALL teamspeak3 groups")
        for user in Teamspeak3User.objects.exclude(uid__exact=''):
            Teamspeak3Tasks.update_groups.delay(user.user_id)

    @staticmethod
    def get_username(user):
        from .auth_hooks import Teamspeak3Service
        return NameFormatter(Teamspeak3Service(), user).format_name()
