import logging

from django.conf import settings
from django.template.loader import render_to_string

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import Phpbb3Tasks
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class Phpbb3Service(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'phpbb3'
        self.urlpatterns = urlpatterns
        self.service_url = settings.PHPBB3_URL
        self.access_perm = 'phpbb3.access_phpbb3'
        self.name_format = '{character_name}'

    @property
    def title(self):
        return 'phpBB3 Forum'

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return Phpbb3Tasks.delete_user(user, notify_user=notify_user)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if Phpbb3Tasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

    def update_groups(self, user):
        logger.debug('Updating %s groups for %s' % (self.name, user))
        if Phpbb3Tasks.has_account(user):
            Phpbb3Tasks.update_groups.delay(user.pk)

    def update_all_groups(self):
        logger.debug('Update all %s groups called' % self.name)
        Phpbb3Tasks.update_all_groups.delay()

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        urls = self.Urls()
        urls.auth_activate = 'phpbb3:activate'
        urls.auth_deactivate = 'phpbb3:deactivate'
        urls.auth_reset_password = 'phpbb3:reset_password'
        urls.auth_set_password = 'phpbb3:set_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.phpbb3.username if Phpbb3Tasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return Phpbb3Service()
