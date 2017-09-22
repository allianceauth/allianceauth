from django.shortcuts import render, get_object_or_404, redirect
from .models import Notification
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger(__name__)


@login_required
def notification_list(request):
    logger.debug("notification_list called by user %s" % request.user)
    new_notifs = Notification.objects.filter(user=request.user).filter(viewed=False)
    old_notifs = Notification.objects.filter(user=request.user).filter(viewed=True)
    logger.debug("User %s has %s unread and %s read notifications" % (request.user, len(new_notifs), len(old_notifs)))
    context = {
        'read': old_notifs,
        'unread': new_notifs,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def notification_view(request, notif_id):
    logger.debug("notification_view called by user %s for notif_id %s" % (request.user, notif_id))
    notif = get_object_or_404(Notification, pk=notif_id)
    if notif.user == request.user:
        logger.debug("Providing notification for user %s" % request.user)
        context = {'notif': notif}
        notif.view()
        return render(request, 'notifications/view.html', context)
    else:
        logger.warn(
            "User %s not authorized to view notif_id %s belonging to user %s" % (request.user, notif_id, notif.user))
        messages.error(request, _('You are not authorized to view that notification.'))
        return redirect('notifications:list')


@login_required
def remove_notification(request, notif_id):
    logger.debug("remove notification called by user %s for notif_id %s" % (request.user, notif_id))
    notif = get_object_or_404(Notification, pk=notif_id)
    if notif.user == request.user:
        if Notification.objects.filter(id=notif_id).exists():
            notif.delete()
            logger.info("Deleting notif id %s by user %s" % (notif_id, request.user))
            messages.success(request, _('Deleted notification.'))
    else:
        logger.error(
            "Unable to delete notif id %s for user %s - notif matching id not found." % (notif_id, request.user))
        messages.error(request, _('Failed to locate notification.'))
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    logger.debug('mark all notifications read called by user %s' % request.user)
    Notification.objects.filter(user=request.user).update(viewed=True)
    messages.success(request, _('Marked all notifications as read.'))
    return redirect('notifications:list')


@login_required
def delete_all_read(request):
    logger.debug('delete all read notifications called by user %s' % request.user)
    Notification.objects.filter(user=request.user).filter(viewed=True).delete()
    messages.success(request, _('Deleted all read notifications.'))
    return redirect('notifications:list')
