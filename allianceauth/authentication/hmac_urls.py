from django.conf.urls import url, include

from allianceauth.authentication import views

urlpatterns = [
    url(r'^activate/complete/$', views.activation_complete, name='registration_activation_complete'),
    # The activation key can make use of any character from the
    # URL-safe base64 alphabet, plus the colon as a separator.
    url(r'^activate/(?P<activation_key>[-:\w]+)/$', views.ActivationView.as_view(), name='registration_activate'),
    url(r'^register/$', views.RegistrationView.as_view(), name='registration_register'),
    url(r'^register/complete/$', views.registration_complete, name='registration_complete'),
    url(r'^register/closed/$', views.registration_closed, name='registration_disallowed'),
    url(r'', include('registration.auth_urls')),
]