from django.db import models
from django.contrib.auth.models import User


class SyncGroupCache(models.Model):
    groupname = models.CharField(max_length=254)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.user.username + ' - ' + self.groupname + ' - SyncGroupCache'
