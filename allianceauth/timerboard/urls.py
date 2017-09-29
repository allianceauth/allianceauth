from django.conf.urls import url

from . import views

app_name = 'timerboard'

urlpatterns = [
    url(r'^$', views.TimerView.as_view(), name='view'),
    url(r'^add/$', views.AddTimerView.as_view(), name='add'),
    url(r'^remove/(?P<pk>\w+)$', views.RemoveTimerView.as_view(), name='delete'),
    url(r'^edit/(?P<pk>\w+)$', views.EditTimerView.as_view(), name='edit'),
]
