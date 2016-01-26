from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo
from datetime import datetime


class optimer(models.Model):
    class Meta:
        ordering = ['start']
    doctrine = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    location = models.CharField(max_length=254, default="")
    start = models.DateTimeField(default=datetime.now)
    duration = models.CharField(max_length=25, default="")
    operation_name = models.CharField(max_length=254, default="")
    fc = models.CharField(max_length=254, default="")
    details = models.CharField(max_length=254, default="")
    post_time = models.DateTimeField(default=timezone.now)
    eve_character = models.ForeignKey(EveCharacter)
    
