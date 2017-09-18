from django.db import models


class Teamspeak3User(models.Model):
    user = models.OneToOneField('auth.User',
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
    auth_group = models.ForeignKey('auth.Group')
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name = 'Auth / TS Group'

    def __str__(self):
        return self.auth_group.name


class UserTSgroup(models.Model):
    user = models.ForeignKey('auth.User')
    ts_group = models.ManyToManyField(TSgroup)

    class Meta:
        verbose_name = 'User TS Group'

    def __str__(self):
        return self.user.name
