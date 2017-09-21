import logging

from .models import CharacterOwnership, UserProfile, get_guest_state, State
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete, m2m_changed, pre_save
from django.dispatch import receiver, Signal
from esi.models import Token

from allianceauth.eveonline.models import EveCharacter

logger = logging.getLogger(__name__)


state_changed = Signal(providing_args=['user', 'state'])


def trigger_state_check(state):
    # evaluate all current members to ensure they still have access
    for profile in state.userprofile_set.all():
        profile.assign_state()

    # we may now be available to others with lower states
    check_states = State.objects.filter(priority__lt=state.priority)
    for profile in UserProfile.objects.filter(state__in=check_states):
        if state.available_to_user(profile.user):
            profile.state = state
            profile.save(update_fields=['state'])
            state_changed.send(sender=state.__class__, user=profile.user, state=state)


@receiver(m2m_changed, sender=State.member_characters.through)
def state_member_characters_changed(sender, instance, action, *args, **kwargs):
    if action.startswith('post_'):
        trigger_state_check(instance)


@receiver(m2m_changed, sender=State.member_corporations.through)
def state_member_corporations_changed(sender, instance, action, *args, **kwargs):
    if action.startswith('post_'):
        trigger_state_check(instance)


@receiver(m2m_changed, sender=State.member_alliances.through)
def state_member_alliances_changed(sender, instance, action, *args, **kwargs):
    if action.startswith('post_'):
        trigger_state_check(instance)


@receiver(post_save, sender=State)
def state_saved(sender, instance, *args, **kwargs):
    trigger_state_check(instance)


# Is there a smarter way to intercept pre_save with a diff main_character or state?
@receiver(post_save, sender=UserProfile)
def reassess_on_profile_save(sender, instance, created, *args, **kwargs):
    # catches post_save from profiles to trigger necessary service and state checks
    if not created:
        update_fields = kwargs.pop('update_fields', []) or []
        if 'state' not in update_fields:
            instance.assign_state()


@receiver(post_save, sender=User)
def create_required_models(sender, instance, created, *args, **kwargs):
    # ensure all users have a model
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Token)
def record_character_ownership(sender, instance, created, *args, **kwargs):
    if created:
        if instance.user:
            query = Q(owner_hash=instance.character_owner_hash) & Q(user=instance.user)
        else:
            query = Q(owner_hash=instance.character_owner_hash)
        # purge ownership records if the hash or auth user account has changed
        CharacterOwnership.objects.filter(character__character_id=instance.character_id).exclude(query).delete()
        # create character if needed
        if EveCharacter.objects.filter(character_id=instance.character_id).exists() is False:
            EveCharacter.objects.create_character(instance.character_id)
        char = EveCharacter.objects.get(character_id=instance.character_id)
        # check if we need to create ownership
        if instance.user and not CharacterOwnership.objects.filter(character__character_id=instance.character_id).exists():
            CharacterOwnership.objects.update_or_create(character=char,
                                                        defaults={'owner_hash': instance.character_owner_hash,
                                                                  'user': instance.user})


@receiver(pre_delete, sender=CharacterOwnership)
def validate_main_character(sender, instance, *args, **kwargs):
    if instance.user.profile.main_character == instance.character:
        # clear main character as user no longer owns them
        instance.user.profile.main_character = None
        instance.user.profile.save()


@receiver(pre_delete, sender=Token)
def validate_main_character_token(sender, instance, *args, **kwargs):
    if UserProfile.objects.filter(main_character__character_id=instance.character_id).exists():
        profile = UserProfile.objects.get(main_character__character_id=instance.character_id)
        if not Token.objects.filter(character_id=instance.character_id).filter(user=profile.user).exclude(pk=instance.pk).exists():
            # clear main character as we can no longer verify ownership
            profile.main_character = None
            profile.save()


@receiver(pre_save, sender=User)
def assign_state_on_active_change(sender, instance, *args, **kwargs):
    # set to guest state if inactive, assign proper state if reactivated
    if instance.pk:
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.is_active != instance.is_active:
            if instance.is_active:
                instance.profile.assign_state()
            else:
                instance.profile.state = get_guest_state()
                instance.profile.save(update_fields=['state'])


@receiver(post_save, sender=EveCharacter)
def check_state_on_character_update(sender, instance, *args, **kwargs):
    # if this is a main character updating, check that user's state
    try:
        instance.userprofile.assign_state()
    except UserProfile.DoesNotExist:
        pass
