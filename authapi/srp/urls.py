from __future__ import unicode_literals

from django.conf.urls import url
import authapi.srp.views

urlpatterns = [
    url(r'^srpfleetmain/$', authapi.srp.views.SrpFleetMainList.as_view(), name='srpfleetmain-list'),
    url(r'^srpfleetmain/(?P<pk>[0-9]+)$', authapi.srp.views.SrpFleetMainDetail.as_view(), name='srpfleetmain-detail'),
    url(r'^srpuserrequest/$', authapi.srp.views.SrpUserRequestList.as_view(), name='srpuserrequest-list'),
    url(r'^srpuserrequest/(?P<pk>[0-9]+)$', authapi.srp.views.SrpUserRequestDetail.as_view(), name='srpuserrequest-detail'),
]
