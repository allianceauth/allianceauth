from django.db import models
from django.contrib.auth.models import Group

class TSgroup(models.Model):
    ts_group_id = models.IntegerField(primary_key=True)
    ts_group_name = models.CharField(max_length=30)

    class Meta:
        verbose_name='TS Group'

    def __str__(self):
        return self.ts_group_name
	
class AuthTS(models.Model):
    auth_group = models.ForeignKey('auth.Group')
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name='Auth / TS Group'

    def __str__(self):
        return self.auth_group.name

class UserTSgroup(models.Model):
    user = models.ForeignKey('auth.User')
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name='User TS Group'

    def __str__(self):
        return self.user.name

class DiscordAuthToken(models.Model):
    email = models.CharField(max_length=254, primary_key=True)
    token = models.CharField(max_length=254)
    def __str__(self):
        return self.email
