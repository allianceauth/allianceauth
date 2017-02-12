from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.db import models


@python_2_unicode_compatible
class DiscordUser(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='discord')
    uid = models.CharField(max_length=254)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.uid)

    class Meta:
        permissions = (
            ("access_discord", u"Can access the Discord service"),
        )
