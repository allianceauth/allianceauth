from django.conf.urls import url, include

from . import views

module_urls = [
    # Mumble service control
    url(r'^activate/$', views.activate_mumble, name='activate'),
    url(r'^deactivate/$', views.deactivate_mumble, name='deactivate'),
    url(r'^reset_password/$', views.reset_mumble_password,
        name='reset_password'),
    url(r'^set_password/$', views.set_mumble_password, name='set_password'),
]

urlpatterns = [
    url(r'^mumble/', include(module_urls, namespace='mumble'))
]
