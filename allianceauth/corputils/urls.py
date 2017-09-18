from django.conf.urls import url

from . import views

app_name = 'corputils'
urlpatterns = [
    url(r'^$', views.corpstats_view, name='view'),
    url(r'^add/$', views.corpstats_add, name='add'),
    url(r'^(?P<corp_id>(\d)*)/$', views.corpstats_view, name='view_corp'),
    url(r'^(?P<corp_id>(\d)+)/update/$', views.corpstats_update, name='update'),
    url(r'^search/$', views.corpstats_search, name='search'),
    ]
