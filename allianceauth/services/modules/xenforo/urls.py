from django.conf.urls import url, include

from . import views

module_urls = [
    # XenForo service control
    url(r'^activate/$', views.activate_xenforo_forum, name='activate'),
    url(r'^deactivate/$', views.deactivate_xenforo_forum, name='deactivate'),
    url(r'^reset_password/$', views.reset_xenforo_password, name='reset_password'),
    url(r'^set_password/$', views.set_xenforo_password, name='set_password'),
]

urlpatterns = [
    url(r'^xenforo/', include(module_urls, namespace='xenforo')),
]
