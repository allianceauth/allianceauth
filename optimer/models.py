from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo


class optimer(models.Model):
    class Meta:
        ordering = ['start_time']
    doctrine = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    location = models.CharField(max_length=254, default="")
    start_time = models.CharField(max_length=254, default="")
    end_time = models.CharField(max_length=254, default="")
    operation_name = models.CharField(max_length=254, default="")
    fc = models.CharField(max_length=254, default="")
    details = models.CharField(max_length=254, default="")
    post_time = models.DateTimeField(default=timezone.now)
    eve_character = models.ForeignKey(EveCharacter)
    
