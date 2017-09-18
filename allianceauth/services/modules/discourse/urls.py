from django.conf.urls import url

from . import views

urlpatterns = [
    # Discourse Service Control
    url(r'^discourse/sso$', views.discourse_sso, name='auth_discourse_sso'),
]
