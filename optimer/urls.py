from django.conf.urls import url
import optimer.views

app_name = 'optimer'

urlpatterns = [
    url(r'^$', optimer.views.optimer_view, name='view'),
    url(r'^add$', optimer.views.add_optimer_view, name='add'),
    url(r'^(\w+)/remove$', optimer.views.remove_optimer, name='remove'),
    url(r'^(\w+)/edit$', optimer.views.edit_optimer, name='edit'),
    ]
