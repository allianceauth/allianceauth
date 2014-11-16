from django.db import models
from django.contrib.auth.models import User

from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo


class Timer(models.Model):
    name = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    planet_moon = models.CharField(max_length=254, default="")
    structure = models.CharField(max_length=254, default="")
    fleet_type = models.CharField(max_length=254, default="")
    eve_time = models.DateTimeField()
    important = models.BooleanField(default=False)
    eve_character = models.ForeignKey(EveCharacter)
    eve_corp = models.ForeignKey(EveCorporationInfo)
    user = models.ForeignKey(User)