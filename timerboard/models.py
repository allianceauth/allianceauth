from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User

from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo


@python_2_unicode_compatible
class Timer(models.Model):
    OBJECTIVE_CHOICES = (
        ('Friendly', 'Friendly'),
        ('Hostile', 'Hostile'),
        ('Neutral', 'Neutral'),
    )

    STRUCTURE_CHOICES = (
        ('I-HUB', 'I-HUB'),
        ('POCO', 'POCO'),
        ('POS[S]', 'POS[S]'),
        ('POS[M]', 'POS[M]'),
        ('POS[L]', 'POS[L]'),
        ('Station', 'Station'),
        ('TCU', 'TCU'),
        ('Other', 'Other'),
    )

    class Meta:
        ordering = ['eve_time']

    details = models.CharField(max_length=254, default="")
    system = models.CharField(max_length=254, default="")
    planet_moon = models.CharField(max_length=254, default="")
    structure = models.CharField(max_length=254, default="", choices=STRUCTURE_CHOICES)
    objective = models.CharField(max_length=254, default="", choices=OBJECTIVE_CHOICES)
    eve_time = models.DateTimeField()
    important = models.BooleanField(default=False)
    eve_character = models.ForeignKey(EveCharacter)
    eve_corp = models.ForeignKey(EveCorporationInfo)
    corp_timer = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    def __str__(self):
        return str(self.system) + ' ' + str(self.objective)
