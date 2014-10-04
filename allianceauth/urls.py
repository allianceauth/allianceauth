from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'allianceauth.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'portal.views.index', name='index'),
    url(r'^characters/', 'portal.views.characters_view', name='characters'),
    url(r'^apikeymanagment/', 'portal.views.apikeymanagment_view', name='apimanagment'),
    url(r'^maincharacterchange/(\d+)/$', 'portal.views.main_character_change', name='main_character_change'),
    url(r'^loginuser/','authentication.views.login_user', name='loginuser'),
    url(r'^logoutuser/','authentication.views.logout_user', name='logoutuser'),
    url(r'^register/', 'registration.views.register', name='register'),
)
