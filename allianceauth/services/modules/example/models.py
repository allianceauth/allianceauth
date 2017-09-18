from django.contrib.auth.models import User
from django.db import models


class ExampleUser(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='example')
    username = models.CharField(max_length=254)

    def __str__(self):
        return self.username
