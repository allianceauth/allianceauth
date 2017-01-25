from __future__ import unicode_literals
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _

from . import views

module_urls = [
    # Jabber Service Control
    url(r'^activate/$', views.activate_jabber, name='auth_activate_openfire'),
    url(r'^deactivate/$', views.deactivate_jabber, name='auth_deactivate_openfire'),
    url(r'^reset_password/$', views.reset_jabber_password, name='auth_reset_openfire_password'),
]

module_i18n_urls = [
    url(_(r'^set_password/$'), views.set_jabber_password, name='auth_set_openfire_password'),
]

urlpatterns = [
    url(r'^openfire/', include(module_urls))
]

urlpatterns += i18n_patterns(
    # Jabber Broadcast
    url(_(r'^services/jabber_broadcast/$'), views.jabber_broadcast_view, name='auth_jabber_broadcast_view'),
    # Jabber
    url(r'openfire/', include(module_i18n_urls))
)
