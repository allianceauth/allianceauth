from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # Discord Service Control
    url(r'^activate/$', views.activate_discord, name='auth_activate_discord'),
    url(r'^deactivate/$', views.deactivate_discord, name='auth_deactivate_discord'),
    url(r'^reset/$', views.reset_discord, name='auth_reset_discord'),
    url(r'^callback/$', views.discord_callback, name='auth_discord_callback'),
    url(r'^add_bot/$', views.discord_add_bot, name='auth_discord_add_bot'),
]

urlpatterns = [
    url(r'^discord/', include(module_urls))
]
