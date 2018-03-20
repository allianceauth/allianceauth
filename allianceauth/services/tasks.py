import logging

import redis
from celery import shared_task
from django.contrib.auth.models import User
from .hooks import ServicesHook
from celery_once import QueueOnce as BaseTask

REDIS_CLIENT = redis.Redis()

logger = logging.getLogger(__name__)


class QueueOnce(BaseTask):
    once = BaseTask.once
    once['graceful'] = True


# http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
def only_one(function=None, key="", timeout=None):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""

        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec


@shared_task(bind=True)
def validate_services(self, pk):
    user = User.objects.get(pk=pk)
    logger.debug('Ensuring user {} has permissions for active services'.format(user))
    # Iterate through services hooks and have them check the validity of the user
    for svc in ServicesHook.get_services():
        try:
            svc.validate_user(user)
        except:
            logger.exception('Exception running validate_user for services module %s on user %s' % (svc, user))


def disable_user(user):
    logger.debug('Disabling all services for user %s' % user)
    for svc in ServicesHook.get_services():
        if svc.service_active_for_user(user):
            svc.delete_user(user)

