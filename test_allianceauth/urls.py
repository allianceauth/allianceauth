from django.conf.urls import url
import allianceauth.urls
from . import views

urlpatterns = allianceauth.urls.urlpatterns

urlpatterns += [
    # Navhelper test urls
    url(r'^main-page/$', views.page, name='p1'),
    url(r'^main-page/sub-section/$', views.page, name='p1-s1'),
    url(r'^second-page/$', views.page, name='p1'),
]


