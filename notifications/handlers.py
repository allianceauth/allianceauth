from __future__ import unicode_literals
import logging

logger = logging.getLogger(__name__)


class NotificationHandler(logging.Handler):
    def emit(self, record):
        from django.contrib.auth.models import User
        from notifications.models import Notification
        for user in User.objects.all():
            if user.has_perm('auth.logging_notifications'):
                notif = Notification()
                notif.user = user
                notif.title = "%s [%s:%s]" % (record.levelname, record.funcName, record.lineno)
                notif.level = str([item[0] for item in Notification.LEVEL_CHOICES if item[1] == record.levelname][0])
                message = record.getMessage()
                if record.exc_text:
                    message += "\n\n"
                    message = message + record.exc_text
                notif.message = message
                notif.save()
