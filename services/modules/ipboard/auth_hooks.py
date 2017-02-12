from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import render_to_string

from services.hooks import ServicesHook
from alliance_auth import hooks

from .urls import urlpatterns
from .tasks import IpboardTasks

import logging

logger = logging.getLogger(__name__)


class IpboardService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'ipboard'
        self.service_url = settings.IPBOARD_ENDPOINT
        self.urlpatterns = urlpatterns
        self.access_perm = 'ipboard.access_ipboard'

    @property
    def title(self):
        return 'IPBoard Forums'

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return IpboardTasks.delete_user(user, notify_user=notify_user)

    def update_groups(self, user):
        logger.debug("Updating %s groups for %s" % (self.name, user))
        if IpboardTasks.has_account(user):
            IpboardTasks.update_groups.delay(user.pk)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if IpboardTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

    def update_all_groups(self):
        logger.debug('Update all %s groups called' % self.name)
        IpboardTasks.update_all_groups.delay()

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        urls = self.Urls()
        urls.auth_activate = 'auth_activate_ipboard'
        urls.auth_deactivate = 'auth_deactivate_ipboard'
        urls.auth_reset_password = 'auth_reset_ipboard_password'
        urls.auth_set_password = 'auth_set_ipboard_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.ipboard.username if IpboardTasks.has_account(request.user) else '',
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return IpboardService()
