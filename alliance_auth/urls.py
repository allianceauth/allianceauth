from django.conf.urls import include, url

from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
import authentication.urls
from authentication import hmac_urls
import authentication.views
import services.views
import groupmanagement.views
import notifications.views
import esi.urls
from alliance_auth import NAME
from alliance_auth.hooks import get_hooks
from django.views.generic.base import TemplateView

admin.site.site_header = NAME


# Functional/Untranslated URL's
urlpatterns = [
    # Locale
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Authentication
    url(r'', include(authentication.urls, namespace='authentication')),
    url(r'^account/login/$', TemplateView.as_view(template_name='public/login.html'), name='auth_login_user'),
    url(r'account/', include(hmac_urls)),

    # Admin urls
    url(r'^admin/', include(admin.site.urls)),

    # SSO
    url(r'^sso/', include(esi.urls, namespace='esi')),
    url(r'^sso/login$', authentication.views.sso_login, name='auth_sso_login'),

    # Notifications
    url(r'^remove_notifications/(\w+)/$', notifications.views.remove_notification, name='auth_remove_notification'),
    url(r'^notifications/mark_all_read/$', notifications.views.mark_all_read, name='auth_mark_all_notifications_read'),
    url(r'^notifications/delete_all_read/$', notifications.views.delete_all_read,
        name='auth_delete_all_read_notifications'),
]

# User viewed/translated URLS
urlpatterns += i18n_patterns(
    # Group management
    url(_(r'^groups/'), groupmanagement.views.groups_view, name='auth_groups'),
    url(_(r'^group/management/'), groupmanagement.views.group_management,
        name='auth_group_management'),
    url(_(r'^group/membership/$'), groupmanagement.views.group_membership,
        name='auth_group_membership'),
    url(_(r'^group/membership/(\w+)/$'), groupmanagement.views.group_membership_list,
        name='auth_group_membership_list'),
    url(_(r'^group/membership/(\w+)/remove/(\w+)/$'), groupmanagement.views.group_membership_remove,
        name='auth_group_membership_remove'),
    url(_(r'^group/request_add/(\w+)'), groupmanagement.views.group_request_add,
        name='auth_group_request_add'),
    url(_(r'^group/request/accept/(\w+)'), groupmanagement.views.group_accept_request,
        name='auth_group_accept_request'),
    url(_(r'^group/request/reject/(\w+)'), groupmanagement.views.group_reject_request,
        name='auth_group_reject_request'),

    url(_(r'^group/request_leave/(\w+)'), groupmanagement.views.group_request_leave,
        name='auth_group_request_leave'),
    url(_(r'group/leave_request/accept/(\w+)'), groupmanagement.views.group_leave_accept_request,
        name='auth_group_leave_accept_request'),
    url(_(r'^group/leave_request/reject/(\w+)'), groupmanagement.views.group_leave_reject_request,
        name='auth_group_leave_reject_request'),

    url(_(r'^services/$'), services.views.services_view, name='auth_services'),

    # Tools
    url(_(r'^tool/fleet_formatter_tool/$'), services.views.fleet_formatter_view,
        name='auth_fleet_format_tool_view'),

    # Notifications
    url(_(r'^notifications/$'), notifications.views.notification_list, name='auth_notification_list'),
    url(_(r'^notifications/(\w+)/$'), notifications.views.notification_view, name='auth_notification_view'),


)

# Append hooked service urls
services = get_hooks('services_hook')
for svc in services:
    urlpatterns += svc().urlpatterns

# Append app urls
app_urls = get_hooks('url_hook')
for app in app_urls:
    urlpatterns += [app().include_pattern]
