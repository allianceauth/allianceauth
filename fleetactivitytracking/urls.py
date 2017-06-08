from django.conf.urls import url
import fleetactivitytracking.views

urlpatterns = [
    # FleetActivityTracking (FAT)
    url(r'^$', fleetactivitytracking.views.fatlink_view, name='view'),
    url(r'^statistics/$', fleetactivitytracking.views.fatlink_statistics_view, name='statistics'),
    url(r'^statistics/corp/(\w+)$', fleetactivitytracking.views.fatlink_statistics_corp_view,
        name='statistics_corp'),
    url(r'^statistics/corp/(?P<corpid>\w+)/(?P<year>[0-9]+)/(?P<month>[0-9]+)/',
        fleetactivitytracking.views.fatlink_statistics_corp_view,
        name='statistics_corp_month'),
    url(r'^statistics/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', fleetactivitytracking.views.fatlink_statistics_view,
        name='statistics_month'),
    url(r'^user/statistics/$', fleetactivitytracking.views.fatlink_personal_statistics_view,
        name='personal_statistics'),
    url(r'^user/statistics/(?P<year>[0-9]+)/$', fleetactivitytracking.views.fatlink_personal_statistics_view,
        name='personal_statistics_year'),
    url(r'^user/statistics/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$',
        fleetactivitytracking.views.fatlink_monthly_personal_statistics_view,
        name='personal_statistics_month'),
    url(r'^user/(?P<char_id>[0-9]+)/statistics/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$',
        fleetactivitytracking.views.fatlink_monthly_personal_statistics_view,
        name='user_statistics_month'),
    url(r'^create/$', fleetactivitytracking.views.create_fatlink_view, name='create'),
    url(r'^modify/$', fleetactivitytracking.views.modify_fatlink_view, name='modify'),
    url(r'^modify/(?P<hash>[a-zA-Z0-9_-]+)/([a-z0-9_-]+)$',
        fleetactivitytracking.views.modify_fatlink_view),
    url(r'^link/$', fleetactivitytracking.views.fatlink_view, name='click_fatlink'),
    url(r'^link/(?P<hash>[a-zA-Z0-9]+)/(?P<fatname>[a-z0-9_-]+)/$',
        fleetactivitytracking.views.click_fatlink_view),
    ]