from .models import Notification


def user_notification_count(request):
    return {'notifications': len(Notification.objects.filter(user__id=request.user.id).filter(viewed=False))}
