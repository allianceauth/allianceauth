from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Main Views
    url(r'^$', 'portal.views.index_view', name='auth_index'),
    url(r'^dashboard/$', 'portal.views.dashboard_view', name='auth_dashboard'),
    url(r'^characters/', 'portal.views.characters_view', name='auth_characters'),
    url(r'^api_key_management/', 'portal.views.api_key_management_view', name='auth_api_key_management'),
    url(r'^services/', 'portal.views.services_view', name='auth_services'),

    # Register
    url(r'^register/', 'registration.views.register', name='auth_register'),

    # Authentication
    url(r'^login_user/', 'authentication.views.login_user', name='auth_login_user'),
    url(r'^logout_user/', 'authentication.views.logout_user', name='auth_logout_user'),

    # None views
    url(r'^main_character_change/(\w+)/$', 'portal.views.main_character_change', name='auth_main_character_change'),
    url(r'^activate_forum/$', 'portal.views.activate_forum', name='auth_activate_forum'),
    url(r'^activate_jabber/$', 'portal.views.activate_jabber', name='auth_activate_jabber'),
    url(r'^activate_mumble/$', 'portal.views.activate_mumble', name='auth_activate_mumble'),
    url(r'^delete_api_pair/(\w+)/$', 'portal.views.api_key_removal', name='auth_api_key_removal')
)
