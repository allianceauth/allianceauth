from __future__ import unicode_literals
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from authentication.models import CharacterOwnership, UserProfile, get_guest_state
from services.tasks import validate_services
from esi.models import Token
from eveonline.managers import EveManager
from eveonline.models import EveCharacter
import logging

logger = logging.getLogger(__name__)


# Is there a smarter way to intercept pre_save with a diff main_character or state?
@receiver(post_save, sender=UserProfile)
def reassess_on_profile_save(sender, instance, created, *args, **kwargs):
    # catches post_save from profiles to trigger necessary service and state checks
    if not created:
        update_fields = kwargs.pop('update_fields', [])
        if 'state' not in update_fields:
            instance.assign_state()
        # TODO: how do we prevent running this twice on profile state change?
        validate_services(instance.user)


@receiver(post_save, sender=User)
def create_required_models(sender, instance, created, *args, **kwargs):
    # ensure all users have a model
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Token)
def record_character_ownership(sender, instance, created, *args, **kwargs):
    if created:
        # purge ownership records if the hash or auth user account has changed
        CharacterOwnership.objects.filter(character__character_id=instance.character_id).exclude(
            owner_hash=instance.owner_hash).exclude(user=instance.user).delete()
        # create character if needed
        if EveCharacter.objects.filter(character_id=instance.character_id).exists() is False:
            EveManager.create_character(instance.character_id)
        char = EveCharacter.objects.get(character_id=instance.character_id)
        CharacterOwnership.objects.update_or_create(character=char,
                                                    defaults={'owner_hash': instance.owner_hash, 'user': instance.user})


@receiver(pre_delete, sender=CharacterOwnership)
def validate_main_character(sender, instance, *args, **kwargs):
    if instance.user.profile.main_character == instance.character:
        # clear main character as user no longer owns them
        instance.user.profile.main_character = None
        instance.user.profile.save()


@receiver(pre_delete, sender=Token)
def validate_main_character_token(sender, instance, *args, **kwargs):
    if UserProfile.objects.filter(main_character__character_id=instance.character_id):
        if not Token.objects.filter(character_id=instance.character_id).filter(user=instance.user).exists():
            # clear main character as we can no longer verify ownership
            instance.user.profile.main_character = None
            instance.user.profile.save()


@receiver(post_save, sender=User)
def assign_state_on_reactivate(sender, instance, *args, **kwargs):
    # There's no easy way to trigger an action upon saving from pre_save signal
    # If we're saving a user and that user is in the Guest state, assume is_active was just set to True and assign state
    if instance.is_active and instance.profile.state == get_guest_state():
        instance.profile.assign_state()
