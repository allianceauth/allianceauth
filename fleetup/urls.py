from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.fleetup_view, name='auth_fleetup_view'),
    url(r'^fittings/$', views.fleetup_fittings, name='auth_fleetup_fittings'),
    url(r'^fittings/(?P<fittingnumber>[0-9]+)/$', views.fleetup_fitting, name='auth_fleetup_fitting'),
    url(r'^doctrines/$', views.fleetup_doctrines, name='auth_fleetup_doctrines'),
    url(r'^characters/$', views.fleetup_characters, name='auth_fleetup_characters'),
    url(r'^doctrines/(?P<doctrinenumber>[0-9]+)/$', views.fleetup_doctrine, name='auth_fleetup_doctrine'),
]
