from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


@python_2_unicode_compatible
class GroupCache(models.Model):
    SERVICE_CHOICES = (
        ("discourse", "discourse"),
        ("discord", "discord"),
    )

    created = models.DateTimeField(auto_now_add=True)
    groups = models.TextField(default={})
    service = models.CharField(max_length=254, choices=SERVICE_CHOICES, unique=True)

    def __str__(self):
        return self.service
