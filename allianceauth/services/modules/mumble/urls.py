from django.conf.urls import url, include

from . import views

app_name = 'mumble'

module_urls = [
    # Mumble service control
    url(r'^activate/$', views.CreateAccountMumbleView.as_view(), name='activate'),
    url(r'^deactivate/$', views.DeleteMumbleView.as_view(), name='deactivate'),
    url(r'^reset_password/$', views.ResetPasswordMumbleView.as_view(), name='reset_password'),
    url(r'^set_password/$', views.SetPasswordMumbleView.as_view(), name='set_password'),
]

urlpatterns = [
    url(r'^mumble/', include((module_urls, app_name), namespace=app_name))
]
