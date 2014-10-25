from django.db import models
from django.contrib.auth.models import User


class HRApplications(models.Model):
    character_name = models.CharField(max_length=254, default="")
    full_api_id = models.CharField(max_length=254, default="")
    full_api_key = models.CharField(max_length=254, default="")
    prefered_corp = models.CharField(max_length=254, default="")
    is_a_spi = models.BooleanField(default=False)
    about = models.TextField(default="")
    extra = models.TextField(default="")

    user = models.ForeignKey(User)


class HRApplicationComment(models.Model):
    date = models.DateTimeField(auto_now=True)
    comment = models.TextField(default="")

    user = models.ForeignKey(User)