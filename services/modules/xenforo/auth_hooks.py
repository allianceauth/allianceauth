from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import render_to_string

from services.hooks import ServicesHook
from alliance_auth import hooks

from .urls import urlpatterns
from .tasks import XenforoTasks

import logging

logger = logging.getLogger(__name__)


class XenforoService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'xenforo'
        self.urlpatterns = urlpatterns
        self.access_perm = 'xenforo.access_xenforo'

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
        urls.auth_activate = 'auth_activate_xenforo'
        urls.auth_deactivate = 'auth_deactivate_xenforo'
        urls.auth_reset_password = 'auth_reset_xenforo_password'
        urls.auth_set_password = 'auth_set_xenforo_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': '',
            'username': request.user.xenforo.username if XenforoTasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return XenforoService()
