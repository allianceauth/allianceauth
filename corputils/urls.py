from django.conf.urls import url
import corputils.views

app_name = 'corputils'
urlpatterns = [
    url(r'^$', corputils.views.corpstats_view, name='view'),
    url(r'^add/$', corputils.views.corpstats_add, name='add'),
    url(r'^(?P<corp_id>(\d)*)/$', corputils.views.corpstats_view, name='view_corp'),
    url(r'^(?P<corp_id>(\d)+)/update/$', corputils.views.corpstats_update, name='update'),
    url(r'^search/$', corputils.views.corpstats_search, name='search'),
    ]
