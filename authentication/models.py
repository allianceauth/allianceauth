from django.db import models
from django.contrib.auth.models import User


class AuthServicesInfo(models.Model):
    ipboard_username = models.CharField(max_length=254, default="")
    ipboard_password = models.CharField(max_length=254, default="")
    forum_username = models.CharField(max_length=254, default="")
    forum_password = models.CharField(max_length=254, default="")
    jabber_username = models.CharField(max_length=254, default="")
    jabber_password = models.CharField(max_length=254, default="")
    mumble_username = models.CharField(max_length=254, default="")
    mumble_password = models.CharField(max_length=254, default="")
    teamspeak3_uid = models.CharField(max_length=254, default="")
    teamspeak3_perm_key = models.CharField(max_length=254, default="")
    discord_username = models.CharField(max_length=254, default="")
    discord_uid = models.CharField(max_length=254, default="")
    main_char_id = models.CharField(max_length=64, default="")
    is_blue = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.user.username + ' - AuthInfo'
