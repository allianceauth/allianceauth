from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


@python_2_unicode_compatible
class TSgroup(models.Model):
    ts_group_id = models.IntegerField(primary_key=True)
    ts_group_name = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'TS Group'

    def __str__(self):
        return self.ts_group_name


@python_2_unicode_compatible
class AuthTS(models.Model):
    auth_group = models.ForeignKey('auth.Group')
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name = 'Auth / TS Group'

    def __str__(self):
        return self.auth_group.name


@python_2_unicode_compatible
class UserTSgroup(models.Model):
    user = models.ForeignKey('auth.User')
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name = 'User TS Group'

    def __str__(self):
        return self.user.name


@python_2_unicode_compatible
class MumbleUser(models.Model):
    username = models.CharField(max_length=254, unique=True)
    pwhash = models.CharField(max_length=40)
    groups = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


@python_2_unicode_compatible
class GroupCache(models.Model):
    SERVICE_CHOICES = (
        ("discourse", "discourse"),
        ("discord", "discord"),
    )

    created = models.DateTimeField(auto_now_add=True)
    groups = models.TextField(default={})
    service = models.CharField(max_length=254, choices=SERVICE_CHOICES, unique=True)

    def __str__(self):
        return self.service
