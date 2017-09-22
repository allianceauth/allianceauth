from django.conf.urls import url, include

from . import views

module_urls = [
    # IPS4 Service Control
    url(r'^activate/$', views.activate_ips4, name='activate'),
    url(r'^deactivate/$', views.deactivate_ips4, name='deactivate'),
    url(r'^reset_password/$', views.reset_ips4_password, name='reset_password'),
    url(r'^set_password/$', views.set_ips4_password, name='set_password'),
]

urlpatterns = [
    url(r'^ips4/', include(module_urls, namespace='ips4'))
]
