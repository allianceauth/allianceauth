from __future__ import unicode_literals

import logging

from celery import task

from alliance_auth.hooks import get_hooks
from authentication.states import MEMBER_STATE, BLUE_STATE
from notifications import notify
import redis

REDIS_CLIENT = redis.Redis()

logger = logging.getLogger(__name__)


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


def deactivate_services(user):
    change = False
    logger.debug("Deactivating services for user %s" % user)
    # Iterate through service hooks and disable users
    for fn in get_hooks('services_hook'):
        svc = fn()
        try:
            if svc.delete_user(user):
                change = True
        except:
            logger.exception('Exception running delete_user for services module %s on user %s' % (svc, user))
    if change:
        notify(user, "Services Disabled", message="Your services accounts have been disabled.", level="danger")


@task(bind=True)
def validate_services(self, user, state):
    if state == MEMBER_STATE:
        setting_string = 'AUTH'
    elif state == BLUE_STATE:
        setting_string = 'BLUE'
    else:
        deactivate_services(user)
        return
    logger.debug('Ensuring user %s services are available to state %s' % (user, state))
    # Iterate through services hooks and have them check the validity of the user
    for fn in get_hooks('services_hook'):
        svc = fn()
        try:
            svc.validate_user(user)
        except:
            logger.exception('Exception running validate_user for services module %s on user %s' % (svc, user))
