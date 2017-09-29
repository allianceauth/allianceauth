from datetime import datetime

from django.db import models
from django.utils import timezone

from allianceauth.eveonline.models import EveCharacter


class OpTimer(models.Model):
    class Meta:
        ordering = ['start']

    doctrine = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    start = models.DateTimeField(default=datetime.now)
    duration = models.CharField(max_length=25, default="")
    operation_name = models.CharField(max_length=254, default="")
    fc = models.CharField(max_length=254, default="")
    post_time = models.DateTimeField(default=timezone.now)
    eve_character = models.ForeignKey(EveCharacter, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.operation_name
