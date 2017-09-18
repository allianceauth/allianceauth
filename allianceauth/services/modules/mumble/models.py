from django.db import models


class MumbleUser(models.Model):
    user = models.OneToOneField('auth.User', related_name='mumble', null=True)
    username = models.CharField(max_length=254, unique=True)
    pwhash = models.CharField(max_length=80)
    hashfn = models.CharField(max_length=20, default='sha1')
    groups = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        permissions = (
            ("access_mumble", u"Can access the Mumble service"),
        )
