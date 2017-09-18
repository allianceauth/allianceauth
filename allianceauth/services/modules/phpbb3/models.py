from django.db import models


class Phpbb3User(models.Model):
    user = models.OneToOneField('auth.User',
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='phpbb3')
    username = models.CharField(max_length=254)

    def __str__(self):
        return self.username

    class Meta:
        permissions = (
            ("access_phpbb3", u"Can access the phpBB3 service"),
        )
