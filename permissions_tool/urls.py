from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^overview/$', views.permissions_overview, name='overview'),
    url(r'^audit/(?P<app_label>[\w\-_]+)/(?P<model>[\w\-_]+)/(?P<codename>[\w\-_]+)/$', views.permissions_audit,
        name='audit'),
]
