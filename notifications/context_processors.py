from .models import Notification

def user_notification_count(request):
    return len(Notification.objects.filter(user=request.user).filter(viewed=False))
