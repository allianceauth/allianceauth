from django.db import models
from django.contrib.auth.models import User


class AuthServicesInfo(models.Model):
    ipboard_username = models.CharField(max_length=254, blank=True, default="")
    ipboard_password = models.CharField(max_length=254, blank=True, default="")
    forum_username = models.CharField(max_length=254, blank=True, default="")
    forum_password = models.CharField(max_length=254, blank=True, default="")
    jabber_username = models.CharField(max_length=254, blank=True, default="")
    jabber_password = models.CharField(max_length=254, blank=True, default="")
    mumble_username = models.CharField(max_length=254, blank=True, default="")
    mumble_password = models.CharField(max_length=254, blank=True, default="")
    teamspeak3_uid = models.CharField(max_length=254, blank=True, default="")
    teamspeak3_perm_key = models.CharField(max_length=254, blank=True, default="")
    discord_uid = models.CharField(max_length=254, blank=True, default="")
    discourse_username = models.CharField(max_length=254, blank=True, default="")
    discourse_password = models.CharField(max_length=254, blank=True, default="")
    ips4_username = models.CharField(max_length=254, blank=True, default="")
    ips4_password = models.CharField(max_length=254, blank=True, default="")
    ips4_id = models.CharField(max_length=254, blank=True, default="")
    smf_username = models.CharField(max_length=254, blank=True, default="")
    smf_password = models.CharField(max_length=254, blank=True, default="")
    market_username = models.CharField(max_length=254, blank=True, default="")
    market_password = models.CharField(max_length=254, blank=True, default="")
    pathfinder_username = models.CharField(max_length=254, blank=True, default="")
    pathfinder_password = models.CharField(max_length=254, blank=True, default="")
    main_char_id = models.CharField(max_length=64, blank=True, default="")
    is_blue = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.user.username + ' - AuthInfo'
