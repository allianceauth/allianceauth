from django.db import models
from django.contrib.auth.models import Group, User

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
    email = models.CharField(max_length=254, unique=True)
    token = models.CharField(max_length=254)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__(self):
        output = "Discord Token for email %s user %s" % (self.email, self.user)
        return output.encode('utf-8')

class MumbleUser(models.Model):
    username = models.CharField(max_length=254, unique=True)
    pwhash = models.CharField(max_length=40)
    groups = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username + ' - ' + str(self.user)
