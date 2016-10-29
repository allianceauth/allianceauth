from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from notifications import notify
from eveonline.models import EveCharacter
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class GroupDescription(models.Model):
    description = models.CharField(max_length=512)
    group = models.OneToOneField(Group)

    def __str__(self):
        return self.group.name + " - Description"


@python_2_unicode_compatible
class GroupRequest(models.Model):
    status = models.CharField(max_length=254, default=_('Pending'))
    leave_request = models.BooleanField(default=0)
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    main_char = models.ForeignKey(EveCharacter)

    def __str__(self):
        return self.user.username + ":" + self.group.name

    def accept(self):
        if self.leave_request:
            self.user.groups.remove(self.group)
            notify(self.user, "Group Leave Request Accepted", level="success",
                   message="Your request to leave %s has been accepted." % self.group)
        else:
            self.user.groups.add(self.group)
            notify(self.user, "Group Application Accepted", level="success",
                   message="Your application to %s has been accepted." % self.group)
        self.delete()

    def reject(self):
        if self.leave_request:
            notify(self.user, "Group Application Accepted", level="success",
                   message="Your application to %s has been accepted." % self.group)
        else:
            notify(self.user, "Group Application Rejected", level="danger",
                   message="Your application to %s has been rejected." % self.group)
        self.delete()

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
