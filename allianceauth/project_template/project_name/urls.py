from django.conf.urls import include, url
from allianceauth import urls

urlpatterns = [
    url(r'', include(urls)),
]
