from django.conf.urls import url, include

from . import views

app_name='seat'

module_urls = [
    # SeAT Service Control
    url(r'^activate/$', views.activate_seat, name='activate'),
    url(r'^deactivate/$', views.deactivate_seat, name='deactivate'),
    url(r'^reset_password/$', views.reset_seat_password, name='reset_password'),
    url(r'^set_password/$', views.set_seat_password, name='set_password'),
]

urlpatterns = [
    url(r'^seat/', include((module_urls, app_name), namespace=app_name)),
]
