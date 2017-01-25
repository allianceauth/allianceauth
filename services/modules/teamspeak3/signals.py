from __future__ import unicode_literals

import logging

from django.db import transaction
from django.db.models.signals import m2m_changed
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .tasks import Teamspeak3Tasks
from .models import AuthTS

logger = logging.getLogger(__name__)


def trigger_all_ts_update():
    logger.debug("Triggering update_all_groups")
    Teamspeak3Tasks.update_all_groups()


@receiver(m2m_changed, sender=AuthTS.ts_group.through)
def m2m_changed_authts_group(sender, instance, action, *args, **kwargs):
    logger.debug("Received m2m_changed from %s ts_group with action %s" % (instance, action))
    if action == "post_add" or action == "post_remove":
        transaction.on_commit(trigger_all_ts_update)


@receiver(post_save, sender=AuthTS)
def post_save_authts(sender, instance, *args, **kwargs):
    logger.debug("Received post_save from %s" % instance)
    transaction.on_commit(trigger_all_ts_update)


@receiver(post_delete, sender=AuthTS)
def post_delete_authts(sender, instance, *args, **kwargs):
    logger.debug("Received post_delete signal from %s" % instance)
    transaction.on_commit(trigger_all_ts_update)
