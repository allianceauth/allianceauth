from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

                       # Admin urls
                       url(r'^admin/', include(admin.site.urls)),

                       # Index
                       url(r'^$', 'portal.views.index_view', name='auth_index'),

                       # Authentication Urls
                       url(r'^login_user/', 'authentication.views.login_user', name='auth_login_user'),
                       url(r'^logout_user/', 'authentication.views.logout_user', name='auth_logout_user'),
                       url(r'^register_user/', 'registration.views.register_user_view', name='auth_register_user'),

                       url(r'^user/password/$', 'django.contrib.auth.views.password_change', name='password_change'),
                       url(r'^user/password/done/$', 'django.contrib.auth.views.password_change_done',
                           name='password_change_done'),
                       url(r'^user/password/reset/$', 'django.contrib.auth.views.password_reset',
                           name='password_reset'),
                       url(r'^user/password/password/reset/done/$', 'django.contrib.auth.views.password_reset_done',
                           name='password_reset_done'),
                       url(r'^user/password/reset/complete/$', 'django.contrib.auth.views.password_reset_complete',
                           name='password_reset_complete'),
                       url(r'^user/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                           'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),

                       # Portal Urls
                       url(r'^dashboard/$', 'portal.views.dashboard_view', name='auth_dashboard'),
                       url(r'^help/$', 'portal.views.help_view', name='auth_help'),

                       # Eveonline Urls
                       url(r'^add_api_key/', 'eveonline.views.add_api_key', name='auth_add_api_key'),
                       url(r'^api_key_management/', 'eveonline.views.api_key_management_view',
                           name='auth_api_key_management'),
                       url(r'^refresh_api_pair/([0-9]+)/$', 'eveonline.views.user_refresh_api', name='auth_user_refresh_api'),
                       url(r'^delete_api_pair/(\w+)/$', 'eveonline.views.api_key_removal', name='auth_api_key_removal'),
                       url(r'^characters/', 'eveonline.views.characters_view', name='auth_characters'),
                       url(r'^main_character_change/(\w+)/$', 'eveonline.views.main_character_change',
                           name='auth_main_character_change'),

                       # Group management
                       url(r'^groups/', 'groupmanagement.views.groups_view', name='auth_groups'),
                       url(r'^group/management/', 'groupmanagement.views.group_management',
                           name='auth_group_management'),
                       url(r'^group/request_add/(\w+)', 'groupmanagement.views.group_request_add',
                           name='auth_group_request_add'),
                       url(r'^group/request/accept/(\w+)', 'groupmanagement.views.group_accept_request',
                           name='auth_group_accept_request'),
                       url(r'^group/request/reject/(\w+)', 'groupmanagement.views.group_reject_request',
                           name='auth_group_reject_request'),

                       url(r'^group/request_leave/(\w+)', 'groupmanagement.views.group_request_leave',
                           name='auth_group_request_leave'),
                       url(r'group/leave_request/accept/(\w+)', 'groupmanagement.views.group_leave_accept_request',
                           name='auth_group_leave_accept_request'),
                       url(r'^group/leave_request/reject/(\w+)', 'groupmanagement.views.group_leave_reject_request',
                           name='auth_group_leave_reject_request'),

                       # HR Application Management
                       url(r'^hr_application_management/', 'hrapplications.views.hr_application_management_view',
                           name="auth_hrapplications_view"),
                       url(r'^hr_application_create/$', 'hrapplications.views.hr_application_create_view',
                           name="auth_hrapplication_create_view"),
                       url(r'^hr_application_create/(\d+)', 'hrapplications.views.hr_application_create_view',
                           name="auth_hrapplication_create_view"),
                       url(r'^hr_application_remove/(\w+)', 'hrapplications.views.hr_application_remove',
                           name="auth_hrapplication_remove"),
                       url(r'hr_application_view/(\w+)', 'hrapplications.views.hr_application_view',
                           name="auth_hrapplication_view"),
                       url(r'hr_application_personal_view/(\w+)', 'hrapplications.views.hr_application_personal_view',
                           name="auth_hrapplication_personal_view"),
                       url(r'hr_application_personal_removal/(\w+)',
                           'hrapplications.views.hr_application_personal_removal',
                           name="auth_hrapplication_personal_removal"),
                       url(r'hr_application_approve/(\w+)', 'hrapplications.views.hr_application_approve',
                           name="auth_hrapplication_approve"),
                       url(r'hr_application_reject/(\w+)', 'hrapplications.views.hr_application_reject',
                           name="auth_hrapplication_reject"),
                       url(r'hr_application_search/', 'hrapplications.views.hr_application_search',
                           name="auth_hrapplication_search"),
                       url(r'hr_mark_in_progress/(\w+)', 'hrapplications.views.hr_application_mark_in_progress',
                           name="auth_hrapplication_mark_in_progress"),


                       # Service Urls
                       url(r'^services/$', 'services.views.services_view', name='auth_services'),
                       url(r'^services/jabber_broadcast/$', 'services.views.jabber_broadcast_view',
                           name='auth_jabber_broadcast_view'),

                       # Forum Service Control
                       url(r'^activate_forum/$', 'services.views.activate_forum', name='auth_activate_forum'),
                       url(r'^deactivate_forum/$', 'services.views.deactivate_forum', name='auth_deactivate_forum'),
                       url(r'^reset_forum_password/$', 'services.views.reset_forum_password',
                           name='auth_reset_forum_password'),
                       url(r'^set_forum_password/$', 'services.views.set_forum_password', name='auth_set_forum_password'),


                       # Jabber Service Control
                       url(r'^activate_jabber/$', 'services.views.activate_jabber', name='auth_activate_jabber'),
                       url(r'^deactivate_jabber/$', 'services.views.deactivate_jabber', name='auth_deactivate_jabber'),
                       url(r'^reset_jabber_password/$', 'services.views.reset_jabber_password',
                           name='auth_reset_jabber_password'),
                       url(r'^set_jabber_password/$', 'services.views.set_jabber_password', name='auth_set_jabber_password'),

                       # Mumble service control
                       url(r'^activate_mumble/$', 'services.views.activate_mumble', name='auth_activate_mumble'),
                       url(r'^deactivate_mumble/$', 'services.views.deactivate_mumble', name='auth_deactivate_mumble'),
                       url(r'^reset_mumble_password/$', 'services.views.reset_mumble_password',
                           name='auth_reset_mumble_password'),
                       url(r'^set_mumble_password/$', 'services.views.set_mumble_password', name='auth_set_mumble_password'),

                       # Ipboard service control
                       url(r'^activate_ipboard/$', 'services.views.activate_ipboard_forum',
                           name='auth_activate_ipboard'),
                       url(r'^deactivate_ipboard/$', 'services.views.deactivate_ipboard_forum',
                           name='auth_deactivate_ipboard'),
                       url(r'^reset_ipboard_password/$', 'services.views.reset_ipboard_password',
                           name='auth_reset_ipboard_password'),
                       url(r'^set_ipboard_password/$', 'services.views.set_ipboard_password', name='auth_set_ipboard_password'),

                       # Teamspeak3 service control
                       url(r'^activate_teamspeak3/$', 'services.views.activate_teamspeak3',
                           name='auth_activate_teamspeak3'),
                       url(r'^deactivate_teamspeak3/$', 'services.views.deactivate_teamspeak3',
                           name='auth_deactivate_teamspeak3'),
                       url(r'reset_teamspeak3_perm/$', 'services.views.reset_teamspeak3_perm',
                           name='auth_reset_teamspeak3_perm'),

                       # Discord Service Control
                       url(r'^activate_discord/$', 'services.views.activate_discord', name='auth_activate_discord'),
                       url(r'^deactivate_discord/$', 'services.views.deactivate_discord', name='auth_deactivate_discord'),
                       url(r'^reset_discord/$', 'services.views.reset_discord', name='auth_reset_discord'),

                       # Tools
                       url(r'^tool/fleet_formatter_tool/$', 'services.views.fleet_formatter_view',
                           name='auth_fleet_format_tool_view'),

                       # Timer URLS
                       url(r'^timers/$', 'timerboard.views.timer_view', name='auth_timer_view'),
                       url(r'^add_timer/$', 'timerboard.views.add_timer_view', name='auth_add_timer_view'),
                       url(r'^remove_timer/(\w+)', 'timerboard.views.remove_timer', name='auth_remove_timer'),
                       url(r'^edit_timer/(\w+)$', 'timerboard.views.edit_timer', name='auth_edit_timer'),

                       # SRP URLS
                       url(r'^srp/$', 'srp.views.srp_management', name='auth_srp_management_view'),
                       url(r'^srp_all/$', 'srp.views.srp_management_all', name='auth_srp_management_all_view'),
                       url(r'^srp_fleet_view/(\w+)$', 'srp.views.srp_fleet_view', name='auth_srp_fleet_view'),
                       url(r'^srp_fleet_add_view/$', 'srp.views.srp_fleet_add_view', name='auth_srp_fleet_add_view'),
                       url(r'^srp_fleet_remove/(\w+)$', 'srp.views.srp_fleet_remove', name='auth_srp_flet_remove'),
                       url(r'^srp_fleet_edit/(\w+)$', 'srp.views.srp_fleet_edit_view', name='auth_srp_fleet_edit_view'),
                       url(r'^srp_fleet_mark_completed/(\w+)', 'srp.views.srp_fleet_mark_completed',
                           name='auth_srp_fleet_mark_completed'),
                       url(r'^srp_fleet_mark_uncompleted/(\w+)', 'srp.views.srp_fleet_mark_uncompleted',
                           name='auth_srp_fleet_mark_uncompleted'),
                       url(r'^srp_request/(\w+)', 'srp.views.srp_request_view', name='auth_srp_request_view'),
                       url(r'^srp_request_remove/(\w+)', 'srp.views.srp_request_remove',
                           name="auth_srp_request_remove"),
                       url(r'srp_request_approve/(\w+)', 'srp.views.srp_request_approve',
                           name='auth_srp_request_approve'),
                       url(r'srp_request_reject/(\w+)', 'srp.views.srp_request_reject', name='auth_srp_request_reject'),
                       url(r'srp_request_amount_update/(\w+)', 'srp.views.srp_request_update_amount_view',
                           name="auth_srp_request_update_amount_view"),

                       #corputils
                       url(r'^corputils/$', 'corputils.views.corp_member_view', name='auth_corputils'),
                       url(r'^corputils/(?P<corpid>[0-9]+)/$', 'corputils.views.corp_member_view'),
                       url(r'^corputils/search/$', 'corputils.views.corputils_search', name="auth_corputils_search"),
                       url(r'^corputils/search/(?P<corpid>[0-9]+)/$', 'corputils.views.corputils_search'),

                       # FLEET FITTINGS
                       url(r'^fits/$', 'services.views.fleet_fits', name='auth_fleet_fits'),

                       # Sig Tracker
                       url(r'^sigtracker/$', 'sigtracker.views.sigtracker_view', name='auth_signature_view'),
                       url(r'^add_signature/$', 'sigtracker.views.add_signature_view', name='auth_add_signature_view'),
                       url(r'^remove_signature/(\w+)', 'sigtracker.views.remove_signature', name='auth_remove_signature'),
                       url(r'^edit_signature/(\w+)$', 'sigtracker.views.edit_signature', name='auth_edit_signature'),

                       # Fleet Operations Timers
                       url(r'^optimer/$', 'optimer.views.optimer_view', name='auth_optimer_view'),
                       url(r'^add_optimer/$', 'optimer.views.add_optimer_view', name='auth_add_optimer_view'),
                       url(r'^remove_optimer/(\w+)', 'optimer.views.remove_optimer', name='auth_remove_optimer'),
                       url(r'^edit_optimer/(\w+)$', 'optimer.views.edit_optimer', name='auth_edit_optimer'),

                       # Notifications
                       url(r'^notifications/$', 'notifications.views.notification_list', name='auth_notification_list'),
                       url(r'^notifications/(\w+)/$', 'notifications.views.notification_view', name='auth_notification_view'),
                       url(r'^remove_notifications/(\w+)/$', 'notifications.views.remove_notification', name='auth_remove_notification'),
)
