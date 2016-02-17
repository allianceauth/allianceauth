from .models import Notification

def notify(user, title, message=None, level='info'):
    notif = Notification()
    notif.user = user
    notif.title = title
    if not message:
        message = Title
    notif.message = message
    notif.level = level
    notif.save()
    logger.info("Created notification %s" % notif
