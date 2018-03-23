import logging
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from allianceauth.authentication.models import UserProfile, State
from allianceauth.eveonline.models import EveCharacter

from .models import AutogroupsConfig

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=AutogroupsConfig)
def pre_save_config(sender, instance, *args, **kwargs):
    """
    Checks if enable was toggled on group config and
    deletes groups if necessary.
    """
    logger.debug("Received pre_save from {}".format(instance))
    if not instance.pk:
        # new model being created
        return
    try:
        old_instance = AutogroupsConfig.objects.get(pk=instance.pk)

        # Check if enable was toggled, delete groups?
        if old_instance.alliance_groups is True and instance.alliance_groups is False:
            instance.delete_alliance_managed_groups()

        if old_instance.corp_groups is True and instance.corp_groups is False:
            instance.delete_corp_managed_groups()
    except AutogroupsConfig.DoesNotExist:
        pass


@receiver(pre_delete, sender=AutogroupsConfig)
def pre_delete_config(sender, instance, *args, **kwargs):
    """
    Delete groups on deleting config
    """
    instance.delete_corp_managed_groups()
    instance.delete_alliance_managed_groups()


@receiver(post_save, sender=UserProfile)
def check_groups_on_profile_update(sender, instance, created, *args, **kwargs):
    """
    Trigger check when main character or state changes.
    """
    AutogroupsConfig.objects.update_groups_for_user(instance.user)


@receiver(m2m_changed, sender=AutogroupsConfig.states.through)
def autogroups_states_changed(sender, instance, action, reverse, model, pk_set, *args, **kwargs):
    """
    Trigger group membership update when a state is added or removed from
    an autogroup config.
    """
    if action.startswith('post_'):
        for pk in pk_set:
            try:
                state = State.objects.get(pk=pk)
                instance.update_group_membership_for_state(state)
            except State.DoesNotExist:
                # Deleted States handled by the profile state change
                pass


@receiver(post_save, sender=EveCharacter)
def check_groups_on_character_update(sender, instance, created, *args, **kwargs):
    if not created:
        try:
            profile = UserProfile.objects.prefetch_related('user').get(main_character_id=instance.pk)
            AutogroupsConfig.objects.update_groups_for_user(profile.user)
        except UserProfile.DoesNotExist:
            pass
