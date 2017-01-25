from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # XenForo service control
    url(r'^activate/$', views.activate_xenforo_forum, name='auth_activate_xenforo'),
    url(r'^deactivate/$', views.deactivate_xenforo_forum, name='auth_deactivate_xenforo'),
    url(r'^reset_password/$', views.reset_xenforo_password, name='auth_reset_xenforo_password'),
    url(r'^set_password/$', views.set_xenforo_password, name='auth_set_xenforo_password'),
]

urlpatterns = [
    url(r'^xenforo/', include(module_urls)),
]
