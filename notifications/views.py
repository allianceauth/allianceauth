from django.shortcuts import render, get_object_or_404
from .models import Notification

@login_required
def notification_list(request):
    logger.debug("notification_list called by user %s" % request.user)
    new_notifs = Notification.objects.filter(user=request.user).filter(read=False)
    old_notifs = Notification.objects.filter(user=request.user).filter(read=True)
    logger.debug("User %s has %s unread and %s read notifications" % (request.user, len(new_notifs), len(old_notifs)))
    context = {
        'read': old_notifs,
        'unread': new_notifs,
    }
    return render(request, 'registered/notification_list.html', context)

@login_required
def notification_view(request, notif_id):
    logger.debug("notification_view called by user %s for notif_id %s" % (request.user, notif_id))
    notif = get_object_or_404(notification, pk=notif_id)
    if notif.user == request.user:
        logger.debug("Providing notification for user %s" % request.user)
        context = {'notification': notif}
        notif.view()
        return render(request, 'registered/notification_view.html', context)
    else:
        logger.warn("User %s not authorized to view notif_id %s belonging to user %s" % (request.user, notif_id, notif.user))
