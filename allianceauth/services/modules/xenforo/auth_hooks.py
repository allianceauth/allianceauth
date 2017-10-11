import logging

from django.template.loader import render_to_string

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import XenforoTasks
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class XenforoService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'xenforo'
        self.urlpatterns = urlpatterns
        self.access_perm = 'xenforo.access_xenforo'
        self.name_format = '{character_name}'

    @property
    def title(self):
        return 'XenForo Forums'

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return XenforoTasks.delete_user(user, notify_user=notify_user)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if XenforoTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        urls = self.Urls()
        urls.auth_activate = 'xenforo:activate'
        urls.auth_deactivate = 'xenforo:deactivate'
        urls.auth_reset_password = 'xenforo:reset_password'
        urls.auth_set_password = 'xenforo:set_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': '',
            'username': request.user.xenforo.username if XenforoTasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return XenforoService()
