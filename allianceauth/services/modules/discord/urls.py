from django.conf.urls import url, include

from . import views

app_name = 'discord'

module_urls = [
    # Discord Service Control
    url(r'^activate/$', views.activate_discord, name='activate'),
    url(r'^deactivate/$', views.deactivate_discord, name='deactivate'),
    url(r'^reset/$', views.reset_discord, name='reset'),
    url(r'^callback/$', views.discord_callback, name='callback'),
    url(r'^add_bot/$', views.discord_add_bot, name='add_bot'),
]

urlpatterns = [
    url(r'^discord/', include((module_urls, app_name), namespace=app_name))
]
