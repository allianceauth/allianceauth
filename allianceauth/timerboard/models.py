from django.contrib.auth.models import User
from django.db import models

from allianceauth.eveonline.models import EveCharacter
from allianceauth.eveonline.models import EveCorporationInfo


class Timer(models.Model):
    class Meta:
        ordering = ['eve_time']

    details = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    planet_moon = models.CharField(max_length=254, default="")
    structure = models.CharField(max_length=254, default="")
    objective = models.CharField(max_length=254, default="")
    eve_time = models.DateTimeField()
    important = models.BooleanField(default=False)
    eve_character = models.ForeignKey(EveCharacter)
    eve_corp = models.ForeignKey(EveCorporationInfo)
    corp_timer = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    def __str__(self):
        return str(self.system) + ' ' + str(self.details)
