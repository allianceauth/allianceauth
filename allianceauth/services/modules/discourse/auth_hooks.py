import logging

from django.template.loader import render_to_string
from django.conf import settings

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import DiscourseTasks
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class DiscourseService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.urlpatterns = urlpatterns
        self.name = 'discourse'
        self.service_ctrl_template = 'services/discourse/discourse_service_ctrl.html'
        self.access_perm = 'discourse.access_discourse'
        self.name_format = '{character_name}'

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return DiscourseTasks.delete_user(user, notify_user=notify_user)

    def update_groups(self, user):
        logger.debug('Processing %s groups for %s' % (self.name, user))
        if DiscourseTasks.has_account(user):
            DiscourseTasks.update_groups.delay(user.pk)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if DiscourseTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

    def update_all_groups(self):
        logger.debug('Update all %s groups called' % self.name)
        DiscourseTasks.update_all_groups.delay()

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        return render_to_string(self.service_ctrl_template, {
            'char': request.user.profile.main_character,
            'DISCOURSE_URL': getattr(settings, 'DISCOURSE_URL', ''),
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return DiscourseService()
