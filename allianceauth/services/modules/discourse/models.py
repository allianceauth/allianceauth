from django.contrib.auth.models import User
from django.db import models


class DiscourseUser(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='discourse')
    enabled = models.BooleanField()

    def __str__(self):
        return self.user.username

    class Meta:
        permissions = (
            ("access_discourse", u"Can access the Discourse service"),
        )
