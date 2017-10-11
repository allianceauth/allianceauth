from django.conf import settings
from django.template.loader import render_to_string

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import Ips4Tasks
from .urls import urlpatterns


class Ips4Service(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'ips4'
        self.urlpatterns = urlpatterns
        self.service_url = settings.IPS4_URL
        self.access_perm = 'ips4.access_ips4'
        self.name_format = '{character_name}'

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
        urls.auth_activate = 'ips4:activate'
        urls.auth_deactivate = 'ips4:deactivate'
        urls.auth_reset_password = 'ips4:reset_password'
        urls.auth_set_password = 'ips4:set_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.ips4.username if Ips4Tasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return Ips4Service()
