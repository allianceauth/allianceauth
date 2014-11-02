from django.db import models
from django.contrib.auth.models import User

from eveonline.models import EveCorporationInfo


class HRApplication(models.Model):
    character_name = models.CharField(max_length=254, default="")
    full_api_id = models.CharField(max_length=254, default="")
    full_api_key = models.CharField(max_length=254, default="")
    is_a_spi = models.CharField(max_length=254, default="")
    about = models.TextField(default="")
    extra = models.TextField(default="")

    corp = models.ForeignKey(EveCorporationInfo)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.character_name + " - Application"


class HRApplicationComment(models.Model):
    date = models.DateTimeField(auto_now=True)
    comment = models.TextField(default="")

    user = models.ForeignKey(User)