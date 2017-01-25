from __future__ import unicode_literals
from django.conf.urls import url, include

module_urls = [
    # Add your module URLs here
]

urlpatterns = [
    url(r'^example/', include(module_urls)),
]
