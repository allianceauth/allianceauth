from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from eveonline.models import EveCharacter


class GroupDescription(models.Model):
    description = models.CharField(max_length=512)
    group = models.ForeignKey(Group, unique=True)

    def __str__(self):
        return self.group.name + " - Description"


class GroupRequest(models.Model):
    status = models.CharField(max_length=254)
    leave_request = models.BooleanField(default=0)
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    main_char = models.ForeignKey(EveCharacter)

    def __str__(self):
        return self.user.username + ":" + self.group.name