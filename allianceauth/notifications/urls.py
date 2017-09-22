from django.conf.urls import url
from . import views

app_name = 'notifications'
# Notifications
urlpatterns = [
    url(r'^remove_notifications/(\w+)/$', views.remove_notification, name='remove'),
    url(r'^notifications/mark_all_read/$', views.mark_all_read, name='mark_all_read'),
    url(r'^notifications/delete_all_read/$', views.delete_all_read, name='delete_all_read'),
    url(r'^notifications/$', views.notification_list, name='list'),
    url(r'^notifications/(\w+)/$', views.notification_view, name='view'),
]
