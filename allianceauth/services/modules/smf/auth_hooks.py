import logging

from django.conf import settings
from django.template.loader import render_to_string

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import SmfTasks
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class SmfService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'smf'
        self.urlpatterns = urlpatterns
        self.service_url = settings.SMF_URL
        self.access_perm = 'smf.access_smf'
        self.name_format = '{character_name}'

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
        urls.auth_activate = 'smf:activate'
        urls.auth_deactivate = 'smf:deactivate'
        urls.auth_reset_password = 'smf:reset_password'
        urls.auth_set_password = 'smf:set_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.smf.username if SmfTasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return SmfService()
