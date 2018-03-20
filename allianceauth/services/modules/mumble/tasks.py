import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from allianceauth.services.tasks import QueueOnce
from .models import MumbleUser

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
    @shared_task(bind=True, name="mumble.update_groups", base=QueueOnce)
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating mumble groups for user %s" % user)
        if MumbleTasks.has_account(user):
            try:
                if not user.mumble.update_groups():
                    raise Exception("Group sync failed")
                logger.debug("Updated user %s mumble groups." % user)
                return True
            except MumbleUser.DoesNotExist:
                logger.info("Mumble group sync failed for {}, user does not have a mumble account".format(user))
            except:
                logger.exception("Mumble group sync failed for %s, retrying in 10 mins" % user)
                raise self.retry(countdown=60 * 10)
        else:
            logger.debug("User %s does not have a mumble account, skipping" % user)
        return False

    @staticmethod
    @shared_task(name="mumble.update_all_groups")
    def update_all_groups():
        logger.debug("Updating ALL mumble groups")
        for mumble_user in MumbleUser.objects.exclude(username__exact=''):
            MumbleTasks.update_groups.delay(mumble_user.user.pk)
