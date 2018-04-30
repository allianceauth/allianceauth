import logging

from .models import CharacterOwnership, UserProfile, get_guest_state, State, OwnershipRecord
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, m2m_changed
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
        logger.debug('State {} member characters changed. Re-evaluating membership.'.format(instance))
        trigger_state_check(instance)


@receiver(m2m_changed, sender=State.member_corporations.through)
def state_member_corporations_changed(sender, instance, action, *args, **kwargs):
    if action.startswith('post_'):
        logger.debug('State {} member corporations changed. Re-evaluating membership.'.format(instance))
        trigger_state_check(instance)


@receiver(m2m_changed, sender=State.member_alliances.through)
def state_member_alliances_changed(sender, instance, action, *args, **kwargs):
    if action.startswith('post_'):
        logger.debug('State {} member alliances changed. Re-evaluating membership.'.format(instance))
        trigger_state_check(instance)


@receiver(post_save, sender=State)
def state_saved(sender, instance, *args, **kwargs):
    logger.debug('State {} saved. Re-evaluating membership.'.format(instance))
    trigger_state_check(instance)


# Is there a smarter way to intercept pre_save with a diff main_character or state?
@receiver(post_save, sender=UserProfile)
def reassess_on_profile_save(sender, instance, created, *args, **kwargs):
    # catches post_save from profiles to trigger necessary service and state checks
    if not created:
        update_fields = kwargs.pop('update_fields', []) or []
        if 'state' not in update_fields:
            logger.debug('Profile for {} saved without state change. Re-evaluating state.'.format(instance.user))
            instance.assign_state()


@receiver(post_save, sender=User)
def create_required_models(sender, instance, created, *args, **kwargs):
    # ensure all users have a model
    if created:
        logger.debug('User {} created. Creating default UserProfile.'.format(instance))
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Token)
def record_character_ownership(sender, instance, created, *args, **kwargs):
    if created:
        logger.debug('New token for {0} character {1} saved. Evaluating ownership.'.format(instance.user,
                                                                                           instance.character_name))
        if instance.user:
            query = Q(owner_hash=instance.character_owner_hash) & Q(user=instance.user)
        else:
            query = Q(owner_hash=instance.character_owner_hash)
        # purge ownership records if the hash or auth user account has changed
        CharacterOwnership.objects.filter(character__character_id=instance.character_id).exclude(query).delete()
        # create character if needed
        if EveCharacter.objects.filter(character_id=instance.character_id).exists() is False:
            logger.debug('Token is for a new character. Creating model for {0} ({1})'.format(instance.character_name,
                                                                                             instance.character_id))
            EveCharacter.objects.create_character(instance.character_id)
        char = EveCharacter.objects.get(character_id=instance.character_id)
        # check if we need to create ownership
        if instance.user and not CharacterOwnership.objects.filter(
                character__character_id=instance.character_id).exists():
            logger.debug("Character {0} is not yet owned. Assigning ownership to {1}".format(instance.character_name,
                                                                                             instance.user))
            CharacterOwnership.objects.update_or_create(character=char,
                                                        defaults={'owner_hash': instance.character_owner_hash,
                                                                  'user': instance.user})


@receiver(pre_delete, sender=CharacterOwnership)
def validate_main_character(sender, instance, *args, **kwargs):
    try:
        if instance.user.profile.main_character == instance.character:
            logger.info("Ownership of a main character {0} has been revoked. Resetting {1} main character.".format(
                instance.character, instance.user))
            # clear main character as user no longer owns them
            instance.user.profile.main_character = None
            instance.user.profile.save()
    except UserProfile.DoesNotExist:
        # a user is being deleted
        pass


@receiver(post_delete, sender=Token)
def validate_ownership(sender, instance, *args, **kwargs):
    if not Token.objects.filter(character_owner_hash=instance.character_owner_hash).filter(refresh_token__isnull=False).exists():
        logger.info("No remaining tokens to validate ownership of character {0}. Revoking ownership.".format(instance.character_name))
        CharacterOwnership.objects.filter(owner_hash=instance.character_owner_hash).delete()


@receiver(pre_save, sender=User)
def assign_state_on_active_change(sender, instance, *args, **kwargs):
    # set to guest state if inactive, assign proper state if reactivated
    if instance.pk:
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.is_active != instance.is_active:
            if instance.is_active:
                logger.debug("User {0} has been activated. Assigning state.".format(instance))
                instance.profile.assign_state()
            else:
                logger.debug(
                    "User {0} has been deactivated. Revoking state and assigning to guest state.".format(instance))
                instance.profile.state = get_guest_state()
                instance.profile.save(update_fields=['state'])


@receiver(post_save, sender=EveCharacter)
def check_state_on_character_update(sender, instance, *args, **kwargs):
    # if this is a main character updating, check that user's state
    try:
        logger.debug("Character {0} has been saved. Assessing owner's state for changes.".format(instance))
        instance.userprofile.assign_state()
    except UserProfile.DoesNotExist:
        logger.debug("Character {0} is not a main character. No state assessment required.".format(instance))
        pass


@receiver(post_save, sender=CharacterOwnership)
def ownership_record_creation(sender, instance, created, *args, **kwargs):
    if created:
        records = OwnershipRecord.objects.filter(owner_hash=instance.owner_hash).filter(character=instance.character)
        if records.exists():
            if records[0].user == instance.user:  # most recent record is sorted first
                logger.debug("Already have ownership record of {0} by user {1}".format(instance.character, instance.user))
                return
        logger.info("Character {0} has a new owner {1}. Creating ownership record.".format(instance.character, instance.user))
        OwnershipRecord.objects.create(user=instance.user, character=instance.character, owner_hash=instance.owner_hash)