import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from allianceauth.services.tasks import QueueOnce
from allianceauth.notifications import notify
from allianceauth.services.hooks import NameFormatter
from .manager import SeatManager
from .models import SeatUser

logger = logging.getLogger(__name__)


class SeatTasks:
    def __init__(self):
        pass

    @staticmethod
    def has_account(user):
        try:
            return user.seat.username != ''
        except ObjectDoesNotExist:
            return False

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user) and SeatManager.disable_user(user.seat.username):
            user.seat.delete()
            logger.info("Successfully deactivated SeAT for user %s" % user)
            if notify_user:
                notify(user, 'SeAT Account Disabled', level='danger')
            return True
        return False

    @staticmethod
    @shared_task(bind=True, name='seat.update_roles', base=QueueOnce)
    def update_roles(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating SeAT roles for user %s" % user)
        if SeatTasks.has_account(user):
            groups = [user.profile.state.name]
            for group in user.groups.all():
                groups.append(str(group.name))
            logger.debug("Updating user %s SeAT roles to %s" % (user, groups))
            try:
                SeatManager.update_roles(user.seat.username, groups)
            except:
                logger.warn("SeAT group sync failed for %s, retrying in 10 mins" % user, exc_info=True)
                raise self.retry(countdown=60 * 10)
            logger.debug("Updated user %s SeAT roles." % user)
        else:
            logger.debug("User %s does not have a SeAT account")

    @staticmethod
    @shared_task
    def update_all_roles():
        logger.debug("Updating ALL SeAT roles")
        for user in SeatUser.objects.all():
            SeatTasks.update_roles.delay(user.user_id)

    @staticmethod
    def deactivate():
        SeatUser.objects.all().delete()

    @staticmethod
    def get_username(user):
        from .auth_hooks import SeatService
        return NameFormatter(SeatService(), user).format_name()
