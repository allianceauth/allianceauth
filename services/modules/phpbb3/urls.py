from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # Forum Service Control
    url(r'^activate/$', views.activate_forum, name='auth_activate_phpbb3'),
    url(r'^deactivate/$', views.deactivate_forum, name='auth_deactivate_phpbb3'),
    url(r'^reset_password/$', views.reset_forum_password, name='auth_reset_phpbb3_password'),
    url(r'^set_password/$', views.set_forum_password, name='auth_set_phpbb3_password'),
]

urlpatterns = [
    url(r'^phpbb3/', include(module_urls))
]
