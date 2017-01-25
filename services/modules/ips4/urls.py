from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # IPS4 Service Control
    url(r'^activate/$', views.activate_ips4, name='auth_activate_ips4'),
    url(r'^deactivate/$', views.deactivate_ips4, name='auth_deactivate_ips4'),
    url(r'^reset_password/$', views.reset_ips4_password, name='auth_reset_ips4_password'),
    url(r'^set_password/$', views.set_ips4_password, name='auth_set_ips4_password'),
]

urlpatterns = [
    url(r'^ips4/', include(module_urls))
]
