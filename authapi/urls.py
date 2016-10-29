from __future__ import unicode_literals

from django.conf.urls import url, include
import authapi.authentication.urls
import authapi.eveonline.urls
import authapi.optimer.urls
import authapi.timerboard.urls
import authapi.srp.urls
import authapi.auth.urls
import authapi.groupmanagement.urls

urlpatterns = [
    url(r'^authentication/', include(authapi.authentication.urls)),
    url(r'^eveonline/', include(authapi.eveonline.urls)),
    url(r'^optimer/', include(authapi.optimer.urls)),
    url(r'^timerboard/', include(authapi.timerboard.urls)),
    url(r'^srp/', include(authapi.srp.urls)),
    url(r'^auth/', include(authapi.auth.urls)),
    url(r'groupmanagement/', include(authapi.groupmanagement.urls)),
]
