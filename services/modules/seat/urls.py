from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # SeAT Service Control
    url(r'^activate/$', views.activate_seat, name='auth_activate_seat'),
    url(r'^deactivate/$', views.deactivate_seat, name='auth_deactivate_seat'),
    url(r'^reset_password/$', views.reset_seat_password, name='auth_reset_seat_password'),
    url(r'^set_password/$', views.set_seat_password, name='auth_set_seat_password'),
]

urlpatterns = [
    url(r'^seat/', include(module_urls)),
]
