from django.conf.urls import url
import timerboard.views

app_name = 'timerboard'

urlpatterns = [
    url(r'^$', timerboard.views.timer_view, name='view'),
    url(r'^add/$', timerboard.views.add_timer_view, name='add'),
    url(r'^remove/(\w+)$', timerboard.views.remove_timer, name='remove'),
    url(r'^edit/(\w+)$', timerboard.views.edit_timer, name='edit'),
    ]
