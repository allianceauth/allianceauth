from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # Mumble service control
    url(r'^activate/$', views.activate_mumble, name='auth_activate_mumble'),
    url(r'^deactivate/$', views.deactivate_mumble, name='auth_deactivate_mumble'),
    url(r'^reset_password/$', views.reset_mumble_password,
        name='auth_reset_mumble_password'),
    url(r'^set_password/$', views.set_mumble_password, name='auth_set_mumble_password'),
]

urlpatterns = [
    url(r'^mumble/', include(module_urls))
]
