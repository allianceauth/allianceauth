from django.conf.urls import url

from . import views

app_name = 'timerboard'

urlpatterns = [
    url(r'^$', views.timer_view, name='view'),
    url(r'^add/$', views.add_timer_view, name='add'),
    url(r'^remove/(\w+)$', views.remove_timer, name='remove'),
    url(r'^edit/(\w+)$', views.edit_timer, name='edit'),
    ]
