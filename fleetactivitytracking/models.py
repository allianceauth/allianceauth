from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User
from eveonline.models import EveCharacter
from django.utils import timezone


def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]


@python_2_unicode_compatible
class Fatlink(models.Model):
    fatdatetime = models.DateTimeField(default=timezone.now)
    duration = models.PositiveIntegerField()
    fleet = models.CharField(max_length=254, default="")
    name = models.CharField(max_length=254)
    hash = models.CharField(max_length=254, unique=True)
    creator = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Fat(models.Model):
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE)
    fatlink = models.ForeignKey(Fatlink)
    system = models.CharField(max_length=30)
    shiptype = models.CharField(max_length=30)
    station = models.CharField(max_length=125)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = (('character', 'fatlink'),)

    def __str__(self):
        output = "Fat-link for %s" % self.character.character_name
        return output.encode('utf-8')
