from django.contrib.auth.models import User
from django.db import models


class Ips4User(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='ips4')
    username = models.CharField(max_length=254)
    id = models.CharField(max_length=254)

    def __str__(self):
        return self.username

    class Meta:
        permissions = (
            ("access_ips4", u"Can access the IPS4 service"),
        )
