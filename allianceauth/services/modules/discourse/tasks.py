import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task

from allianceauth.notifications import notify
from allianceauth.services.hooks import NameFormatter
from allianceauth.services.tasks import QueueOnce
from .manager import DiscourseManager
from .models import DiscourseUser

logger = logging.getLogger(__name__)


class DiscourseTasks:
    def __init__(self):
        pass

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user) and user.discourse.enabled:
            logger.debug("User %s has a Discourse account. Disabling login." % user)
            if DiscourseManager.disable_user(user):
                user.discourse.delete()
                if notify_user:
                    notify(user, 'Discourse Account Disabled', level='danger')
                return True
        return False

    @staticmethod
    def has_account(user):
        """
        Check if the user has a discourse account
        :param user: django.contrib.auth.models.User
        :return: bool
        """
        try:
            return user.discourse.enabled
        except ObjectDoesNotExist:
            return False

    @staticmethod
    @shared_task(bind=True, name='discourse.update_groups', base=QueueOnce)
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating discourse groups for user %s" % user)
        try:
            DiscourseManager.update_groups(user)
        except:
            logger.warn("Discourse group sync failed for %s, retrying in 10 mins" % user)
            raise self.retry(countdown=60 * 10)
        logger.debug("Updated user %s discourse groups." % user)

    @staticmethod
    @shared_task(name='discourse.update_all_groups')
    def update_all_groups():
        logger.debug("Updating ALL discourse groups")
        for discourse_user in DiscourseUser.objects.filter(enabled=True):
            DiscourseTasks.update_groups.delay(discourse_user.user.pk)

    @staticmethod
    def get_username(user):
        from .auth_hooks import DiscourseService
        return NameFormatter(DiscourseService(), user).format_name()
