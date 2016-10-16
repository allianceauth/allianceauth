from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from eveonline.models import EveCharacter


@python_2_unicode_compatible
class GroupDescription(models.Model):
    description = models.CharField(max_length=512)
    group = models.OneToOneField(Group)

    def __str__(self):
        return self.group.name + " - Description"


@python_2_unicode_compatible
class GroupRequest(models.Model):
    status = models.CharField(max_length=254)
    leave_request = models.BooleanField(default=0)
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    main_char = models.ForeignKey(EveCharacter)

    def __str__(self):
        return self.user.username + ":" + self.group.name


@python_2_unicode_compatible
class HiddenGroup(models.Model):
    group = models.OneToOneField(Group)

    def __str__(self):
        return self.group.name + " - Hidden"


@python_2_unicode_compatible
class OpenGroup(models.Model):
    group = models.OneToOneField(Group)

    def __str__(self):
        return self.group.name + " - Open"
