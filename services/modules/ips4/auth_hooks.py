from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import render_to_string

from services.hooks import ServicesHook
from alliance_auth import hooks

from .urls import urlpatterns
from .tasks import Ips4Tasks


class Ips4Service(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'ips4'
        self.urlpatterns = urlpatterns
        self.service_url = settings.IPS4_URL
        self.access_perm = 'ips4.access_ips4'

    @property
    def title(self):
        return 'IPS4'

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        """
        Example for rendering the service control panel row
        You can override the default template and create a
        custom one if you wish.
        :param request:
        :return:
        """
        urls = self.Urls()
        urls.auth_activate = 'auth_activate_ips4'
        urls.auth_deactivate = 'auth_deactivate_ips4'
        urls.auth_reset_password = 'auth_reset_ips4_password'
        urls.auth_set_password = 'auth_set_ips4_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.ips4.username if Ips4Tasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return Ips4Service()
