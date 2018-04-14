from django.conf.urls import url, include

from . import views

app_name = 'teamspeak3'

module_urls = [
    # Teamspeak3 service control
    url(r'^activate/$', views.activate_teamspeak3,
        name='activate'),
    url(r'^deactivate/$', views.deactivate_teamspeak3,
        name='deactivate'),
    url(r'^reset_perm/$', views.reset_teamspeak3_perm,
        name='reset_perm'),

    # Teamspeak Urls
    url(r'^verify/$', views.verify_teamspeak3, name='verify'),
]

urlpatterns = [
    url(r'^teamspeak3/', include((module_urls, app_name), namespace=app_name)),
]
