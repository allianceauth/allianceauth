from django.conf.urls import url, include

from . import views

app_name = 'phpbb3'

module_urls = [
    # Forum Service Control
    url(r'^activate/$', views.activate_forum, name='activate'),
    url(r'^deactivate/$', views.deactivate_forum, name='deactivate'),
    url(r'^reset_password/$', views.reset_forum_password, name='reset_password'),
    url(r'^set_password/$', views.set_forum_password, name='set_password'),
]

urlpatterns = [
    url(r'^phpbb3/', include((module_urls, app_name), namespace=app_name))
]
