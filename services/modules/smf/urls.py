from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # SMF Service Control
    url(r'^activate/$', views.activate_smf, name='auth_activate_smf'),
    url(r'^deactivate/$', views.deactivate_smf, name='auth_deactivate_smf'),
    url(r'^reset_password/$', views.reset_smf_password, name='auth_reset_smf_password'),
    url(r'^set_password/$', views.set_smf_password, name='auth_set_smf_password'),
]

urlpatterns = [
    url(r'^smf/', include(module_urls)),
]
