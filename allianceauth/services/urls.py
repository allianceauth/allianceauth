from django.conf.urls import include, url
from allianceauth.hooks import get_hooks

from . import views

urlpatterns = [
    # Services
    url(r'^services/', include(([
        url(r'^$', views.services_view, name='services'),
        # Tools
        url(r'^tool/fleet_formatter_tool/$', views.fleet_formatter_view, name='fleet_format_tool'),
    ], 'services'), namespace='services')),
]

# Append hooked service urls
services = get_hooks('services_hook')
for svc in services:
    urlpatterns += svc().urlpatterns
