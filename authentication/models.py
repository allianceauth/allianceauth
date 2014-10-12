from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class AuthServicesInfo(models.Model):
    forum_username = models.CharField(max_length=254, default="")
    forum_password = models.CharField(max_length=254, default="")
    jabber_username = models.CharField(max_length=254, default="")
    jabber_password = models.CharField(max_length=254, default="")
    mumble_username = models.CharField(max_length=254, default="")
    mumble_password = models.CharField(max_length=254, default="")
    main_char_id = models.CharField(max_length=64, default="")

    user = models.ForeignKey(User)
