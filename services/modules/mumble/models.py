from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


@python_2_unicode_compatible
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
