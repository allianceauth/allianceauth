from django.conf.urls import url, include

from . import views

app_name = 'openfire'

module_urls = [
    # Jabber Service Control
    url(r'^activate/$', views.activate_jabber, name='activate'),
    url(r'^deactivate/$', views.deactivate_jabber, name='deactivate'),
    url(r'^reset_password/$', views.reset_jabber_password, name='reset_password'),
    url(r'^set_password/$', views.set_jabber_password, name='set_password'),
    url(r'^broadcast/$', views.jabber_broadcast_view, name='broadcast'),
]

urlpatterns = [
    url(r'^openfire/', include((module_urls, app_name), namespace=app_name)),
]
