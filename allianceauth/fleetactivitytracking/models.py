from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from allianceauth.eveonline.models import EveCharacter


def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]


class Fatlink(models.Model):
    fatdatetime = models.DateTimeField(default=timezone.now)
    duration = models.PositiveIntegerField()
    fleet = models.CharField(max_length=254)
    hash = models.CharField(max_length=254, unique=True)
    creator = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return self.fleet


class Fat(models.Model):
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE)
    fatlink = models.ForeignKey(Fatlink, on_delete=models.CASCADE)
    system = models.CharField(max_length=30)
    shiptype = models.CharField(max_length=30)
    station = models.CharField(max_length=125)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('character', 'fatlink'),)

    def __str__(self):
        return "Fat-link for %s" % self.character.character_name
