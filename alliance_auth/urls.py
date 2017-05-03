from django.conf.urls import include, url

from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
import django.contrib.auth.views
import authentication.views
import eveonline.views
import services.views
import groupmanagement.views
import optimer.views
import timerboard.views
import fleetactivitytracking.views
import fleetup.views
import srp.views
import notifications.views
import hrapplications.views
import corputils.urls
import esi.urls
import permissions_tool.urls
from alliance_auth import NAME

admin.site.site_header = NAME

from alliance_auth.hooks import get_hooks

# Functional/Untranslated URL's
urlpatterns = [
    # Locale
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Admin urls
    url(r'^admin/', include(admin.site.urls)),

    # SSO
    url(r'^sso/', include(esi.urls, namespace='esi')),
    url(r'^sso/login$', authentication.views.sso_login, name='auth_sso_login'),

    # Index
    url(_(r'^$'), authentication.views.index_view, name='auth_index'),

    # Authentication
    url(r'^logout_user/', authentication.views.logout_user, name='auth_logout_user'),

    # Eve Online
    url(r'^main_character_change/(\w+)/$', eveonline.views.main_character_change,
        name='auth_main_character_change'),
    url(r'^api_verify_owner/(\w+)/$', eveonline.views.api_sso_validate, name='auth_api_sso'),

    # SRP URLS
    url(r'^srp_fleet_remove/(\w+)$', srp.views.srp_fleet_remove, name='auth_srp_fleet_remove'),
    url(r'^srp_fleet_disable/(\w+)$', srp.views.srp_fleet_disable, name='auth_srp_fleet_disable'),
    url(r'^srp_fleet_enable/(\w+)$', srp.views.srp_fleet_enable, name='auth_srp_fleet_enable'),
    url(r'^srp_fleet_mark_completed/(\w+)', srp.views.srp_fleet_mark_completed,
        name='auth_srp_fleet_mark_completed'),
    url(r'^srp_fleet_mark_uncompleted/(\w+)', srp.views.srp_fleet_mark_uncompleted,
        name='auth_srp_fleet_mark_uncompleted'),
    url(r'^srp_request_remove/', srp.views.srp_request_remove,
        name="auth_srp_request_remove"),
    url(r'srp_request_approve/', srp.views.srp_request_approve,
        name='auth_srp_request_approve'),
    url(r'srp_request_reject/', srp.views.srp_request_reject, 
        name='auth_srp_request_reject'),
    url(_(r'srp_request_amount_update/(\w+)'), srp.views.srp_request_update_amount,
        name="auth_srp_request_update_amount"),

    # Notifications
    url(r'^remove_notifications/(\w+)/$', notifications.views.remove_notification, name='auth_remove_notification'),
    url(r'^notifications/mark_all_read/$', notifications.views.mark_all_read, name='auth_mark_all_notifications_read'),
    url(r'^notifications/delete_all_read/$', notifications.views.delete_all_read,
        name='auth_delete_all_read_notifications'),
]

# User viewed/translated URLS
urlpatterns += i18n_patterns(

    # Fleetup
    url(r'^fleetup/$', fleetup.views.fleetup_view, name='auth_fleetup_view'),
    url(r'^fleetup/fittings/$', fleetup.views.fleetup_fittings, name='auth_fleetup_fittings'),
    url(r'^fleetup/fittings/(?P<fittingnumber>[0-9]+)/$', fleetup.views.fleetup_fitting, name='auth_fleetup_fitting'),
    url(r'^fleetup/doctrines/$', fleetup.views.fleetup_doctrines, name='auth_fleetup_doctrines'),
    url(r'^fleetup/characters/$', fleetup.views.fleetup_characters, name='auth_fleetup_characters'),
    url(r'^fleetup/doctrines/(?P<doctrinenumber>[0-9]+)/$', fleetup.views.fleetup_doctrine, name='auth_fleetup_doctrine'),

    # Authentication
    url(_(r'^login_user/'), authentication.views.login_user, name='auth_login_user'),
    url(_(r'^register_user/'), authentication.views.register_user_view, name='auth_register_user'),

    url(_(r'^user/password/$'), django.contrib.auth.views.password_change, name='password_change'),
    url(_(r'^user/password/done/$'), django.contrib.auth.views.password_change_done,
        name='password_change_done'),
    url(_(r'^user/password/reset/$'), django.contrib.auth.views.password_reset,
        name='password_reset'),
    url(_(r'^user/password/password/reset/done/$'), django.contrib.auth.views.password_reset_done,
        name='password_reset_done'),
    url(_(r'^user/password/reset/complete/$'), django.contrib.auth.views.password_reset_complete,
        name='password_reset_complete'),
    url(_(r'^user/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$'),
        django.contrib.auth.views.password_reset_confirm, name='password_reset_confirm'),

    # Portal Urls
    url(_(r'^dashboard/$'), eveonline.views.dashboard_view, name='auth_dashboard'),
    url(_(r'^help/$'), authentication.views.help_view, name='auth_help'),

    # Eveonline Urls
    url(_(r'^add_api_key/'), eveonline.views.add_api_key, name='auth_add_api_key'),
    url(_(r'^refresh_api_pair/([0-9]+)/$'), eveonline.views.user_refresh_api, name='auth_user_refresh_api'),
    url(_(r'^delete_api_pair/(\w+)/$'), eveonline.views.api_key_removal, name='auth_api_key_removal'),
    url(_(r'^characters/'), eveonline.views.characters_view, name='auth_characters'),
    
    # Corputils
    url(_(r'^corpstats/'), include(corputils.urls, namespace='corputils')),

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

    # HR Application Management
    url(_(r'^hr_application_management/'), hrapplications.views.hr_application_management_view,
        name="auth_hrapplications_view"),
    url(_(r'^hr_application_create/$'), hrapplications.views.hr_application_create_view,
        name="auth_hrapplication_create_view"),
    url(_(r'^hr_application_create/(\d+)'), hrapplications.views.hr_application_create_view,
        name="auth_hrapplication_create_view"),
    url(_(r'^hr_application_remove/(\w+)'), hrapplications.views.hr_application_remove,
        name="auth_hrapplication_remove"),
    url(_(r'hr_application_view/(\w+)'), hrapplications.views.hr_application_view,
        name="auth_hrapplication_view"),
    url(_(r'hr_application_personal_view/(\w+)'), hrapplications.views.hr_application_personal_view,
        name="auth_hrapplication_personal_view"),
    url(_(r'hr_application_personal_removal/(\w+)'),
        hrapplications.views.hr_application_personal_removal,
        name="auth_hrapplication_personal_removal"),
    url(_(r'hr_application_approve/(\w+)'), hrapplications.views.hr_application_approve,
        name="auth_hrapplication_approve"),
    url(_(r'hr_application_reject/(\w+)'), hrapplications.views.hr_application_reject,
        name="auth_hrapplication_reject"),
    url(_(r'hr_application_search/'), hrapplications.views.hr_application_search,
        name="auth_hrapplication_search"),
    url(_(r'hr_mark_in_progress/(\w+)'), hrapplications.views.hr_application_mark_in_progress,
        name="auth_hrapplication_mark_in_progress"),

    # Fleet Operations Timers
    url(_(r'^optimer/$'), optimer.views.optimer_view, name='auth_optimer_view'),
    url(_(r'^add_optimer/$'), optimer.views.add_optimer_view, name='auth_add_optimer_view'),
    url(_(r'^remove_optimer/(\w+)'), optimer.views.remove_optimer, name='auth_remove_optimer'),
    url(_(r'^edit_optimer/(\w+)$'), optimer.views.edit_optimer, name='auth_edit_optimer'),

    # Service Urls
    url(_(r'^services/$'), services.views.services_view, name='auth_services'),

    # Timer URLS
    url(_(r'^timers/$'), timerboard.views.timer_view, name='auth_timer_view'),
    url(_(r'^add_timer/$'), timerboard.views.add_timer_view, name='auth_add_timer_view'),
    url(_(r'^remove_timer/(\w+)'), timerboard.views.remove_timer, name='auth_remove_timer'),
    url(_(r'^edit_timer/(\w+)$'), timerboard.views.edit_timer, name='auth_edit_timer'),

    # SRP URLS
    url(_(r'^srp/$'), srp.views.srp_management, name='auth_srp_management_view'),
    url(_(r'^srp_all/$'), srp.views.srp_management_all, name='auth_srp_management_all_view'),
    url(_(r'^srp_fleet_view/(\w+)$'), srp.views.srp_fleet_view, name='auth_srp_fleet_view'),
    url(_(r'^srp_fleet_add_view/$'), srp.views.srp_fleet_add_view, name='auth_srp_fleet_add_view'),
    url(_(r'^srp_fleet_edit/(\w+)$'), srp.views.srp_fleet_edit_view, name='auth_srp_fleet_edit_view'),
    url(_(r'^srp_request/(\w+)'), srp.views.srp_request_view, name='auth_srp_request_view'),

    # Tools
    url(_(r'^tool/fleet_formatter_tool/$'), services.views.fleet_formatter_view,
        name='auth_fleet_format_tool_view'),

    # Notifications
    url(_(r'^notifications/$'), notifications.views.notification_list, name='auth_notification_list'),
    url(_(r'^notifications/(\w+)/$'), notifications.views.notification_view, name='auth_notification_view'),

    # FleetActivityTracking (FAT)
    url(r'^fat/$', fleetactivitytracking.views.fatlink_view, name='auth_fatlink_view'),
    url(r'^fat/statistics/$', fleetactivitytracking.views.fatlink_statistics_view, name='auth_fatlink_view_statistics'),
    url(r'^fat/statistics/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', fleetactivitytracking.views.fatlink_statistics_view,
        name='auth_fatlink_view_statistics_month'),
    url(r'^fat/user/statistics/$', fleetactivitytracking.views.fatlink_personal_statistics_view,
        name='auth_fatlink_view_personal_statistics'),
    url(r'^fat/user/statistics/(?P<year>[0-9]+)/$', fleetactivitytracking.views.fatlink_personal_statistics_view,
        name='auth_fatlink_view_personal_statistics_year'),
    url(r'^fat/user/statistics/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$',
        fleetactivitytracking.views.fatlink_monthly_personal_statistics_view,
        name='auth_fatlink_view_personal_statistics_month'),
    url(r'^fat/user/(?P<char_id>[0-9]+)/statistics/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$',
        fleetactivitytracking.views.fatlink_monthly_personal_statistics_view,
        name='auth_fatlink_view_user_statistics_month'),
    url(r'^fat/create/$', fleetactivitytracking.views.create_fatlink_view, name='auth_create_fatlink_view'),
    url(r'^fat/modify/$', fleetactivitytracking.views.modify_fatlink_view, name='auth_modify_fatlink_view'),
    url(r'^fat/modify/(?P<hash>[a-zA-Z0-9_-]+)/([a-z0-9_-]+)$',
        fleetactivitytracking.views.modify_fatlink_view),
    url(r'^fat/link/$', fleetactivitytracking.views.fatlink_view, name='auth_click_fatlink_view'),
    url(r'^fat/link/(?P<hash>[a-zA-Z0-9]+)/(?P<fatname>[a-z0-9_-]+)/$',
        fleetactivitytracking.views.click_fatlink_view),

    url(r'^permissions/', include(permissions_tool.urls))
)

# Append hooked service urls
services = get_hooks('services_hook')
for svc in services:
    urlpatterns += svc().urlpatterns

