import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from allianceauth.services.tasks import QueueOnce
from allianceauth.notifications import notify
from allianceauth.services.hooks import NameFormatter
from .manager import Phpbb3Manager
from .models import Phpbb3User

logger = logging.getLogger(__name__)


class Phpbb3Tasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            logger.debug("User %s has forum account %s. Deleting." % (user, user.phpbb3.username))
            if Phpbb3Manager.disable_user(user.phpbb3.username):
                user.phpbb3.delete()
                if notify_user:
                    notify(user, 'Forum Account Disabled', level='danger')
                return True
        return False

    @staticmethod
    def has_account(user):
        try:
            return user.phpbb3.username != ''
        except ObjectDoesNotExist:
            return False

    @staticmethod
    @shared_task(bind=True, name="phpbb3.update_groups", base=QueueOnce)
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating phpbb3 groups for user %s" % user)
        if Phpbb3Tasks.has_account(user):
            groups = [user.profile.state.name]
            for group in user.groups.all():
                groups.append(str(group.name))
            logger.debug("Updating user %s phpbb3 groups to %s" % (user, groups))
            try:
                Phpbb3Manager.update_groups(user.phpbb3.username, groups)
            except:
                logger.exception("Phpbb group sync failed for %s, retrying in 10 mins" % user)
                raise self.retry(countdown=60 * 10)
            logger.debug("Updated user %s phpbb3 groups." % user)
        else:
            logger.debug("User does not have a Phpbb3 account")

    @staticmethod
    @shared_task(name="phpbb3.update_all_groups")
    def update_all_groups():
        logger.debug("Updating ALL phpbb3 groups")
        for user in Phpbb3User.objects.exclude(username__exact=''):
            Phpbb3Tasks.update_groups.delay(user.user_id)

    @staticmethod
    def disable():
        Phpbb3User.objects.all().delete()

    @staticmethod
    def get_username(user):
        from .auth_hooks import Phpbb3Service
        return NameFormatter(Phpbb3Service(), user).format_name()
