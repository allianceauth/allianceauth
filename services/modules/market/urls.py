from __future__ import unicode_literals
from django.conf.urls import url, include

from . import views

module_urls = [
    # Alliance Market Control
    url(r'^activate/$', views.activate_market, name='auth_activate_market'),
    url(r'^deactivate/$', views.deactivate_market, name='auth_deactivate_market'),
    url(r'^reset_password/$', views.reset_market_password, name='auth_reset_market_password'),
    url(r'^set_password/$', views.set_market_password, name='auth_set_market_password'),
]

urlpatterns = [
    url(r'^evernus-market/', include(module_urls))
]
