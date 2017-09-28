from django.conf.urls import url, include

from . import views

app_name = 'evernusmarket'

module_urls = [
    # Alliance Market Control
    url(r'^activate/$', views.activate_market, name='activate'),
    url(r'^deactivate/$', views.deactivate_market, name='deactivate'),
    url(r'^reset_password/$', views.reset_market_password, name='reset_password'),
    url(r'^set_password/$', views.set_market_password, name='set_password'),
]

urlpatterns = [
    url(r'^evernus-market/', include((module_urls, app_name), namespace=app_name))
]
