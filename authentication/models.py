from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User, Permission
from authentication.managers import CharacterOwnershipManager, StateManager
from eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo


@python_2_unicode_compatible
class State(models.Model):
    name = models.CharField(max_length=20, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    priority = models.IntegerField(unique=True)

    member_characters = models.ManyToManyField(EveCharacter)
    member_corporations = models.ManyToManyField(EveCorporationInfo)
    member_alliances = models.ManyToManyField(EveAllianceInfo)
    public = models.BooleanField(default=False)

    objects = StateManager()

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.name


def get_guest_state():
    return State.objects.update_or_create(name='Guest', defaults={'priority': 0, 'public': True})[0]


@python_2_unicode_compatible
class UserProfile(models.Model):
    class Meta:
        default_permissions = ('change',)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    main_character = models.OneToOneField(EveCharacter, blank=True, null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, on_delete=models.SET(get_guest_state))

    def assign_state(self, commit=True):
        self.state = State.objects.get_for_user(self.user)
        if commit:
            self.save(update_fields=['state'])

    def __str__(self):
        return "%s Profile" % self.user


@python_2_unicode_compatible
class CharacterOwnership(models.Model):
    class Meta:
        default_permissions = ('change', 'delete')

    character = models.OneToOneField(EveCharacter, on_delete=models.CASCADE, related_name='character_ownership')
    owner_hash = models.CharField(max_length=28, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='character_ownerships')

    objects = CharacterOwnershipManager()

    def __str__(self):
        return "%s: %s" % (self.user, self.character)
