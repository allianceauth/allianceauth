from django.conf.urls import url

from . import views

app_name = 'fleetup'

urlpatterns = [
    url(r'^$', views.fleetup_view, name='view'),
    url(r'^fittings/$', views.fleetup_fittings, name='fittings'),
    url(r'^fittings/(?P<fittingnumber>[0-9]+)/$', views.fleetup_fitting, name='fitting'),
    url(r'^doctrines/$', views.fleetup_doctrines, name='doctrines'),
    url(r'^characters/$', views.fleetup_characters, name='characters'),
    url(r'^doctrines/(?P<doctrinenumber>[0-9]+)/$', views.fleetup_doctrine, name='doctrine'),
]
