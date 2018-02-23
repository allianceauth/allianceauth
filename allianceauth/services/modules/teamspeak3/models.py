from django.db import models
from django.contrib.auth.models import User, Group
from allianceauth.authentication.models import State


class Teamspeak3User(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='teamspeak3')
    uid = models.CharField(max_length=254)
    perm_key = models.CharField(max_length=254)

    def __str__(self):
        return self.uid

    class Meta:
        permissions = (
            ("access_teamspeak3", u"Can access the Teamspeak3 service"),
        )


class TSgroup(models.Model):
    ts_group_id = models.IntegerField(primary_key=True)
    ts_group_name = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'TS Group'

    def __str__(self):
        return self.ts_group_name


class AuthTS(models.Model):
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name = 'Auth / TS Group'

    def __str__(self):
        return self.auth_group.name


class UserTSgroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name = 'User TS Group'

    def __str__(self):
        return self.user.name


class StateGroup(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    ts_group = models.ForeignKey(TSgroup, on_delete=models.CASCADE)
