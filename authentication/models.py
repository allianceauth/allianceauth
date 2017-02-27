from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User
from authentication.states import MEMBER_STATE, BLUE_STATE, NONE_STATE
from eveonline.models import EveCharacter


@python_2_unicode_compatible
class AuthServicesInfo(models.Model):
    class Meta:
        default_permissions = ('change',)

    STATE_CHOICES = (
        (NONE_STATE, 'None'),
        (BLUE_STATE, 'Blue'),
        (MEMBER_STATE, 'Member'),
    )

    main_char_id = models.CharField(max_length=64, blank=True, default="")
    user = models.OneToOneField(User)
    state = models.CharField(blank=True, null=True, choices=STATE_CHOICES, default=NONE_STATE, max_length=10)

    def __str__(self):
        return self.user.username + ' - AuthInfo'


@python_2_unicode_compatible
class State(models.Model):
    name = models.CharField(_('name'), max_length=20, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )
    priority = models.IntegerField(unique=True)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.name


def get_none_state():
    return State.objects.get_or_create(name='None')[0]


@python_2_unicode_compatible
class UserProfile(models.Model):
    class Meta:
        default_permissions = ('change',)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    main_character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.SET(get_none_state))
    owner_hash = models.CharField(max_length=28, unique=True)
    owner_token = models.ForeignKey(Token, on_delete=models.SET_NULL)
