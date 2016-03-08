from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo


class sigtracker(models.Model):
    class Meta:
        ordering = ['post_time']
    ident = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    destination = models.CharField(max_length=254, default="")
    lifetime_status = models.CharField(max_length=254, default="")
    mass_status = models.CharField(max_length=254, default="")
    ships_size = models.CharField(max_length=254, default="")
    notes = models.CharField(max_length=254, default="")
    through_dest = models.CharField(max_length=254, default="")
    post_time = models.DateTimeField(default=timezone.now)
    eve_character = models.ForeignKey(EveCharacter)
    
    
