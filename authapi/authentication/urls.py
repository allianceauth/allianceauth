from __future__ import unicode_literals

import authapi.authentication.views
from django.conf.urls import url

urlpatterns = [
    url(r'^authservicesinfo/$', authapi.authentication.views.AuthServicesInfoList.as_view(), name='authservicesinfo-list'),
    url(r'^authservicesinfo/(?P<pk>[0-9]+)$', authapi.authentication.views.AuthServicesInfoDetail.as_view(), name='authservicesinfo-detail'),
]
