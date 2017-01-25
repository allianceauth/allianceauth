from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # Ipboard service control
    url(r'^activate/$', views.activate_ipboard_forum, name='auth_activate_ipboard'),
    url(r'^deactivate/$', views.deactivate_ipboard_forum, name='auth_deactivate_ipboard'),
    url(r'^reset_password/$', views.reset_ipboard_password, name='auth_reset_ipboard_password'),
    url(r'^set_password/$', views.set_ipboard_password, name='auth_set_ipboard_password'),
]

urlpatterns = [
    url(r'^ipboard/', include(module_urls))
]
