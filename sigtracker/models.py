from django.db import models
from django.contrib.auth.models import User

from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo


class sigtracker(models.Model):
    class Meta:
        ordering = ['sigtype']
    ident = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    destination = models.CharField(max_length=254, default="")
    sigtype = models.CharField(max_length=254, default="")
    status = models.CharField(max_length=254, default="")
    notes = models.CharField(max_length=254, default="")

    
