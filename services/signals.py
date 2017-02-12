from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver

from alliance_auth.hooks import get_hooks
from authentication.tasks import disable_user
from authentication.tasks import set_state

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_user_groups(sender, instance, action, *args, **kwargs):
    logger.debug("Received m2m_changed from %s groups with action %s" % (instance, action))

    def trigger_service_group_update():
        logger.debug("Triggering service group update for %s" % instance)
        # Iterate through Service hooks
        services = get_hooks('services_hook')
        for fn in services:
            svc = fn()
            try:
                svc.update_groups(instance)
            except:
                logger.exception('Exception running update_groups for services module %s on user %s' % (svc, instance))

    if instance.pk and (action == "post_add" or action == "post_remove" or action == "post_clear"):
        logger.debug("Waiting for commit to trigger service group update for %s" % instance)
        transaction.on_commit(trigger_service_group_update)


@receiver(pre_delete, sender=User)
def pre_delete_user(sender, instance, *args, **kwargs):
    logger.debug("Received pre_delete from %s" % instance)
    disable_user(instance)


@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, *args, **kwargs):
    logger.debug("Received pre_save from %s" % instance)
    # check if user is being marked active/inactive
    if not instance.pk:
        # new model being created
        return
    try:
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.is_active and not instance.is_active:
            logger.info("Disabling services for inactivation of user %s" % instance)
            disable_user(instance)
        elif instance.is_active and not old_instance.is_active:
            logger.info("Assessing state of reactivated user %s" % instance)
            set_state(instance)
    except User.DoesNotExist:
        pass
