from django.conf.urls import url

from . import views

app_name = 'optimer'

urlpatterns = [
    url(r'^$', views.optimer_view, name='view'),
    url(r'^add$', views.add_optimer_view, name='add'),
    url(r'^(\w+)/remove$', views.remove_optimer, name='remove'),
    url(r'^(\w+)/edit$', views.edit_optimer, name='edit'),
    ]
