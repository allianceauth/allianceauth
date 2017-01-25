from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # Teamspeak3 service control
    url(r'^activate/$', views.activate_teamspeak3,
        name='auth_activate_teamspeak3'),
    url(r'^deactivate/$', views.deactivate_teamspeak3,
        name='auth_deactivate_teamspeak3'),
    url(r'reset_perm/$', views.reset_teamspeak3_perm,
        name='auth_reset_teamspeak3_perm'),

    # Teamspeak Urls
    url(r'verify/$', views.verify_teamspeak3, name='auth_verify_teamspeak3'),
]

urlpatterns = [
    url(r'^teamspeak3/', include(module_urls)),
]
