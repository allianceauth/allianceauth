default_app_config = 'allianceauth.notifications.apps.NotificationsConfig'
import logging

logger = logging.getLogger(__name__)

MAX_NOTIFICATIONS = 50


def notify(user, title, message=None, level='info'):
    from .models import Notification
    if Notification.objects.filter(user=user).count() > MAX_NOTIFICATIONS:
        for n in Notification.objects.filter(user=user)[MAX_NOTIFICATIONS-1:]:
            n.delete()
    notif = Notification()
    notif.user = user
    notif.title = title
    if not message:
        message = title
    notif.message = message
    notif.level = level
    notif.save()
    logger.info("Created notification %s" % notif)
