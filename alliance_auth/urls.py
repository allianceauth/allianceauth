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
    url(r'^user/password/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^user/password/reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^user/password/password/reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^user/password/reset/complete/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
    url(r'^user/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),

    # Portal Urls
    url(r'^dashboard/$', 'portal.views.dashboard_view', name='auth_dashboard'),
    url(r'^help/$', 'portal.views.help_view', name='auth_help'),

    # Eveonline Urls
    url(r'^add_api_key/', 'eveonline.views.add_api_key', name='auth_add_api_key'),
    url(r'^api_key_management/', 'eveonline.views.api_key_management_view', name='auth_api_key_management'),
    url(r'^delete_api_pair/(\w+)/$', 'eveonline.views.api_key_removal', name='auth_api_key_removal'),
    url(r'^characters/', 'eveonline.views.characters_view', name='auth_characters'),
    url(r'^main_character_change/(\w+)/$', 'eveonline.views.main_character_change', name='auth_main_character_change'),

    # Service Urls
    url(r'^services/', 'services.views.services_view', name='auth_services'),

    # Forum Service Control
    url(r'^activate_forum/$', 'services.views.activate_forum', name='auth_activate_forum'),
    url(r'^deactivate_forum/$', 'services.views.deactivate_forum', name='auth_deactivate_forum'),
    url(r'reset_forum_password/$', 'services.views.reset_forum_password', name='auth_reset_forum_password'),

    # Jabber Service Control
    url(r'^activate_jabber/$', 'services.views.activate_jabber', name='auth_activate_jabber'),
    url(r'^deactivate_jabber/$', 'services.views.deactivate_jabber', name='auth_deactivate_jabber'),
    url(r'^reset_jabber_password/$', 'services.views.reset_jabber_password', name='auth_reset_jabber_password'),

    # Mumble service contraol
    url(r'^activate_mumble/$', 'services.views.activate_mumble', name='auth_activate_mumble'),
    url(r'deactivate_mumble/$', 'services.views.deactivate_mumble', name='auth_deactivate_mumble'),
    url(r'reset_mumble_password/$', 'services.views.reset_mumble_password', name='auth_reset_mumble_password'),
)
