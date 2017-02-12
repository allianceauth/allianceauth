from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import render_to_string

from services.hooks import ServicesHook
from alliance_auth import hooks

from .urls import urlpatterns
from .tasks import SmfTasks

import logging

logger = logging.getLogger(__name__)


class SmfService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'smf'
        self.urlpatterns = urlpatterns
        self.service_url = settings.SMF_URL
        self.access_perm = 'smf.access_smf'

    @property
    def title(self):
        return 'SMF Forums'

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return SmfTasks.delete_user(user, notify_user=notify_user)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if SmfTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user)

    def update_groups(self, user):
        logger.debug('Updating %s groups for %s' % (self.name, user))
        if SmfTasks.has_account(user):
            SmfTasks.update_groups.delay(user.pk)

    def update_all_groups(self):
        logger.debug('Update all %s groups called' % self.name)
        SmfTasks.update_all_groups.delay()

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        urls = self.Urls()
        urls.auth_activate = 'auth_activate_smf'
        urls.auth_deactivate = 'auth_deactivate_smf'
        urls.auth_reset_password = 'auth_reset_smf_password'
        urls.auth_set_password = 'auth_set_smf_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.smf.username if SmfTasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return SmfService()
