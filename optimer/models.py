from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.utils import timezone
from eveonline.models import EveCharacter
from datetime import datetime


@python_2_unicode_compatible
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

    def __str__(self):
        output = self.operation_name
        return output.encode('utf-8')
