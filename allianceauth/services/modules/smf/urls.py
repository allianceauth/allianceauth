from django.conf.urls import url, include

from . import views

app_name = 'smf'

module_urls = [
    # SMF Service Control
    url(r'^activate/$', views.activate_smf, name='activate'),
    url(r'^deactivate/$', views.deactivate_smf, name='deactivate'),
    url(r'^reset_password/$', views.reset_smf_password, name='reset_password'),
    url(r'^set_password/$', views.set_smf_password, name='set_password'),
]

urlpatterns = [
    url(r'^smf/', include((module_urls, app_name), namespace=app_name)),
]
