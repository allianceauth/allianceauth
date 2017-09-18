from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


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
    timestamp = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    def view(self):
        logger.info("Marking notification as viewed: %s" % self)
        self.viewed = True
        self.save()

    def __str__(self):
        return "%s: %s" % (self.user, self.title)

    def set_level(self, level):
        self.level = [item[0] for item in self.LEVEL_CHOICES if item[1] == level][0]

    class Meta:
        ordering = ['-timestamp']
