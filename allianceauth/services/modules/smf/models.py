from django.db import models


class SmfUser(models.Model):
    user = models.OneToOneField('auth.User',
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='smf')
    username = models.CharField(max_length=254)

    def __str__(self):
        return self.username

    class Meta:
        permissions = (
            ("access_smf", u"Can access the SMF service"),
        )
