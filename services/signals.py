from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User, Group, Permission
from django.db import transaction
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver

from services.hooks import ServicesHook
from alliance_auth.hooks import get_hooks
from authentication.tasks import disable_user
from authentication.tasks import disable_member
from authentication.tasks import set_state

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_user_groups(sender, instance, action, *args, **kwargs):
    logger.debug("Received m2m_changed from %s groups with action %s" % (instance, action))

    def trigger_service_group_update():
        logger.debug("Triggering service group update for %s" % instance)
        # Iterate through Service hooks
        for svc in ServicesHook.get_services():
            try:
                svc.validate_user(instance)
                svc.update_groups(instance)
            except:
                logger.exception('Exception running update_groups for services module %s on user %s' % (svc, instance))

    if instance.pk and (action == "post_add" or action == "post_remove" or action == "post_clear"):
        logger.debug("Waiting for commit to trigger service group update for %s" % instance)
        transaction.on_commit(trigger_service_group_update)


@receiver(m2m_changed, sender=User.user_permissions.through)
def m2m_changed_user_permissions(sender, instance, action, *args, **kwargs):
    logger.debug("Received m2m_changed from user %s permissions with action %s" % (instance, action))
    logger.debug('sender: %s' % sender)
    if instance.pk and (action == "post_remove" or action == "post_clear"):
        logger.debug("Permissions changed for user {}, re-validating services".format(instance))
        # Checking permissions for a single user is quite fast, so we don't need to validate
        # That the permissions is a service permission, unlike groups.

        def validate_all_services():
            logger.debug("Validating all services for user {}".format(instance))
            for svc in ServicesHook.get_services():
                try:
                    svc.validate_user(instance)
                except:
                    logger.exception(
                        'Exception running validate_user for services module {} on user {}'.format(svc, user))

        transaction.on_commit(lambda: validate_all_services())


@receiver(m2m_changed, sender=Group.permissions.through)
def m2m_changed_group_permissions(sender, instance, action, pk_set, *args, **kwargs):
    logger.debug("Received m2m_changed from group %s permissions with action %s" % (instance, action))
    if instance.pk and (action == "post_remove" or action == "post_clear"):
        logger.debug("Checking if service permission changed for group {}".format(instance))
        # As validating an entire groups service could lead to many thousands of permission checks
        # first we check that one of the permissions changed is, in fact, a service permission.
        perms = Permission.objects.filter(pk__in=pk_set)
        got_change = False
        service_perms = [svc.access_perm for svc in ServicesHook.get_services()]
        for perm in perms:
            natural_key = perm.natural_key()
            path_perm = "{}.{}".format(natural_key[1], natural_key[0])
            if path_perm not in service_perms:
                # Not a service permission, keep searching
                continue
            for svc in ServicesHook.get_services():
                if svc.access_perm == path_perm:
                    logger.debug("Permissions changed for group {} on "
                                 "service {}, re-validating services for groups users".format(instance, svc))

                    def validate_all_groups_users_for_service():
                        logger.debug("Performing validation for service {}".format(svc))
                        for user in instance.user_set.all():
                            svc.validate_user(user)

                    transaction.on_commit(validate_all_groups_users_for_service)
                    got_change = True
                    break  # Found service, break out of services iteration and go back to permission iteration
        if not got_change:
            logger.debug("Permission change for group {} was not service permission, ignoring".format(instance))


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
