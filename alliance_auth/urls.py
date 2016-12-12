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
import corputils.views
import fleetactivitytracking.views
import fleetup.views
import srp.views
import notifications.views
import hrapplications.views
import esi.urls

# Functional/Untranslated URL's
urlpatterns = [
    # Locale
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Admin urls
    url(r'^admin/', include(admin.site.urls)),

    # SSO
    url (r'^sso/', include(esi.urls, namespace='esi')),
    url (r'^sso/login$', authentication.views.sso_login, name='auth_sso_login'),

    # Index
    url(_(r'^$'), authentication.views.index_view, name='auth_index'),

    # Authentication
    url(r'^logout_user/', authentication.views.logout_user, name='auth_logout_user'),

    # Eve Online
    url(r'^main_character_change/(\w+)/$', eveonline.views.main_character_change,
        name='auth_main_character_change'),
    url(r'^api_verify_owner/(\w+)/$', eveonline.views.api_sso_validate, name='auth_api_sso'),

    # Forum Service Control
    url(r'^activate_forum/$', services.views.activate_forum, name='auth_activate_forum'),
    url(r'^deactivate_forum/$', services.views.deactivate_forum, name='auth_deactivate_forum'),
    url(r'^reset_forum_password/$', services.views.reset_forum_password,
        name='auth_reset_forum_password'),
    url(r'^set_forum_password/$', services.views.set_forum_password, name='auth_set_forum_password'),

    # Jabber Service Control
    url(r'^activate_jabber/$', services.views.activate_jabber, name='auth_activate_jabber'),
    url(r'^deactivate_jabber/$', services.views.deactivate_jabber, name='auth_deactivate_jabber'),
    url(r'^reset_jabber_password/$', services.views.reset_jabber_password,
        name='auth_reset_jabber_password'),

    # Mumble service control
    url(r'^activate_mumble/$', services.views.activate_mumble, name='auth_activate_mumble'),
    url(r'^deactivate_mumble/$', services.views.deactivate_mumble, name='auth_deactivate_mumble'),
    url(r'^reset_mumble_password/$', services.views.reset_mumble_password,
        name='auth_reset_mumble_password'),
    url(r'^set_mumble_password/$', services.views.set_mumble_password, name='auth_set_mumble_password'),

    # Ipboard service control
    url(r'^activate_ipboard/$', services.views.activate_ipboard_forum,
        name='auth_activate_ipboard'),
    url(r'^deactivate_ipboard/$', services.views.deactivate_ipboard_forum,
        name='auth_deactivate_ipboard'),
    url(r'^reset_ipboard_password/$', services.views.reset_ipboard_password,
        name='auth_reset_ipboard_password'),
    url(r'^set_ipboard_password/$', services.views.set_ipboard_password, name='auth_set_ipboard_password'),

    # XenForo service control
    url(r'^activate_xenforo/$', services.views.activate_xenforo_forum,
        name='auth_activate_xenforo'),
    url(r'^deactivate_xenforo/$', services.views.deactivate_xenforo_forum,
        name='auth_deactivate_xenforo'),
    url(r'^reset_xenforo_password/$', services.views.reset_xenforo_password,
        name='auth_reset_xenforo_password'),
    url(r'^set_xenforo_password/$', services.views.set_xenforo_password, name='auth_set_xenforo_password'),

    # Teamspeak3 service control
    url(r'^activate_teamspeak3/$', services.views.activate_teamspeak3,
        name='auth_activate_teamspeak3'),
    url(r'^deactivate_teamspeak3/$', services.views.deactivate_teamspeak3,
        name='auth_deactivate_teamspeak3'),
    url(r'reset_teamspeak3_perm/$', services.views.reset_teamspeak3_perm,
        name='auth_reset_teamspeak3_perm'),

    # Discord Service Control
    url(r'^activate_discord/$', services.views.activate_discord, name='auth_activate_discord'),
    url(r'^deactivate_discord/$', services.views.deactivate_discord, name='auth_deactivate_discord'),
    url(r'^reset_discord/$', services.views.reset_discord, name='auth_reset_discord'),
    url(r'^discord_callback/$', services.views.discord_callback, name='auth_discord_callback'),
    url(r'^discord_add_bot/$', services.views.discord_add_bot, name='auth_discord_add_bot'),

    # Discourse Service Control
    url(r'^discourse_sso$', services.views.discourse_sso, name='auth_discourse_sso'),

    # IPS4 Service Control
    url(r'^activate_ips4/$', services.views.activate_ips4,
        name='auth_activate_ips4'),
    url(r'^deactivate_ips4/$', services.views.deactivate_ips4,
        name='auth_deactivate_ips4'),
    url(r'^reset_ips4_password/$', services.views.reset_ips4_password,
        name='auth_reset_ips4_password'),
    url(r'^set_ips4_password/$', services.views.set_ips4_password, name='auth_set_ips4_password'),

    # SMF Service Control
    url(r'^activate_smf/$', services.views.activate_smf, name='auth_activate_smf'),
    url(r'^deactivate_smf/$', services.views.deactivate_smf, name='auth_deactivate_smf'),
    url(r'^reset_smf_password/$', services.views.reset_smf_password,
        name='auth_reset_smf_password'),
    url(r'^set_smf_password/$', services.views.set_smf_password, name='auth_set_smf_password'),

    # Alliance Market Control
    url(r'^activate_market/$', services.views.activate_market, name='auth_activate_market'),
    url(r'^deactivate_market/$', services.views.deactivate_market, name='auth_deactivate_market'),
    url(r'^reset_market_password/$', services.views.reset_market_password,
        name='auth_reset_market_password'),
    url(r'^set_market_password/$', services.views.set_market_password, name='auth_set_market_password'),

    # SRP URLS
    url(r'^srp_fleet_remove/(\w+)$', srp.views.srp_fleet_remove, name='auth_srp_fleet_remove'),
    url(r'^srp_fleet_disable/(\w+)$', srp.views.srp_fleet_disable, name='auth_srp_fleet_disable'),
    url(r'^srp_fleet_enable/(\w+)$', srp.views.srp_fleet_enable, name='auth_srp_fleet_enable'),
    url(r'^srp_fleet_mark_completed/(\w+)', srp.views.srp_fleet_mark_completed,
        name='auth_srp_fleet_mark_completed'),
    url(r'^srp_fleet_mark_uncompleted/(\w+)', srp.views.srp_fleet_mark_uncompleted,
        name='auth_srp_fleet_mark_uncompleted'),
    url(r'^srp_request_remove/(\w+)', srp.views.srp_request_remove,
        name="auth_srp_request_remove"),
    url(r'srp_request_approve/(\w+)', srp.views.srp_request_approve,
        name='auth_srp_request_approve'),
    url(r'srp_request_reject/(\w+)', srp.views.srp_request_reject, name='auth_srp_request_reject'),

    # Notifications
    url(r'^remove_notifications/(\w+)/$', notifications.views.remove_notification, name='auth_remove_notification'),
    url(r'^notifications/mark_all_read/$', notifications.views.mark_all_read, name='auth_mark_all_notifications_read'),
    url(r'^notifications/delete_all_read/$', notifications.views.delete_all_read,
        name='auth_delete_all_read_notifications'),
]

# User viewed/translated URLS
urlpatterns += i18n_patterns(

    # corputils
    url(r'^corputils/$', corputils.views.corp_member_view, name='auth_corputils'),
    url(r'^corputils/(?P<corpid>[0-9]+)/$', corputils.views.corp_member_view, name='auth_corputils_corp_view'),
    url(r'^corputils/(?P<corpid>[0-9]+)/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', corputils.views.corp_member_view,
        name='auth_corputils_month'),
    url(r'^corputils/search/$', corputils.views.corputils_search, name="auth_corputils_search"),
    url(r'^corputils/search/(?P<corpid>[0-9]+)/$', corputils.views.corputils_search, name='auth_corputils_search_corp'),

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
    url(_(r'^dashboard/$'), authentication.views.dashboard_view, name='auth_dashboard'),
    url(_(r'^help/$'), authentication.views.help_view, name='auth_help'),

    # Eveonline Urls
    url(_(r'^add_api_key/'), eveonline.views.add_api_key, name='auth_add_api_key'),
    url(_(r'^api_key_management/'), eveonline.views.api_key_management_view,
        name='auth_api_key_management'),
    url(_(r'^refresh_api_pair/([0-9]+)/$'), eveonline.views.user_refresh_api, name='auth_user_refresh_api'),
    url(_(r'^delete_api_pair/(\w+)/$'), eveonline.views.api_key_removal, name='auth_api_key_removal'),
    url(_(r'^characters/'), eveonline.views.characters_view, name='auth_characters'),

    # Group management
    url(_(r'^groups/'), groupmanagement.views.groups_view, name='auth_groups'),
    url(_(r'^group/management/'), groupmanagement.views.group_management,
        name='auth_group_management'),
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
    url(_(r'^services/jabber_broadcast/$'), services.views.jabber_broadcast_view,
        name='auth_jabber_broadcast_view'),

    # Teamspeak Urls
    url(r'verify_teamspeak3/$', services.views.verify_teamspeak3, name='auth_verify_teamspeak3'),

    # corputils
    url(_(r'^corputils/$'), corputils.views.corp_member_view, name='auth_corputils'),
    url(_(r'^corputils/(?P<corpid>[0-9]+)/$'), corputils.views.corp_member_view, name='auth_corputils_corp_view'),
    url(_(r'^corputils/search/$'), corputils.views.corputils_search, name="auth_corputils_search"),
    url(_(r'^corputils/search/(?P<corpid>[0-9]+)/$'), corputils.views.corputils_search, name='auth_corputils_search_corp'),

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
    url(_(r'srp_request_amount_update/(\w+)'), srp.views.srp_request_update_amount_view,
        name="auth_srp_request_update_amount_view"),

    # Tools
    url(_(r'^tool/fleet_formatter_tool/$'), services.views.fleet_formatter_view,
        name='auth_fleet_format_tool_view'),

    # Notifications
    url(_(r'^notifications/$'), notifications.views.notification_list, name='auth_notification_list'),
    url(_(r'^notifications/(\w+)/$'), notifications.views.notification_view, name='auth_notification_view'),

    # Jabber
    url(_(r'^set_jabber_password/$'), services.views.set_jabber_password, name='auth_set_jabber_password'),

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
)
