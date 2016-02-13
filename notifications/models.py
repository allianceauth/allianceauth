from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):

    LEVEL_CHOICES = (
        ('danger', 'CRITICAL'),
        ('danger', 'ERROR'),
        ('warning', 'WARN'),
        ('info', 'INFO'),
        ('success', 'DEBUG'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.CharField(choices=LEVEL_CHOICES, max_length=10)
    title = models.CharField(max_length=254)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField()

    def view(self):
        logger.info("Marking notification as viewed: %s" % self)
        self.viewed = True
        self.save()

    def __unicode__(self):
        output = "%s: %s" % (self.user, self.title)
        return output.encode('utf-8')
