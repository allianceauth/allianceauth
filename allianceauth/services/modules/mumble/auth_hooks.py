import logging

from django.conf import settings
from django.template.loader import render_to_string
from allianceauth.notifications import notify

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import MumbleTasks
from .models import MumbleUser
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class MumbleService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'mumble'
        self.urlpatterns = urlpatterns
        self.service_url = settings.MUMBLE_URL
        self.access_perm = 'mumble.access_mumble'
        self.service_ctrl_template = 'services/mumble/mumble_service_ctrl.html'
        self.name_format = '[{corp_ticker}]{character_name}'

    def delete_user(self, user, notify_user=False):
        logging.debug("Deleting user %s %s account" % (user, self.name))
        try:
            if user.mumble.delete():
                if notify_user:
                    notify(user, 'Mumble Account Disabled', level='danger')
                return True
            return False
        except MumbleUser.DoesNotExist:
            logging.debug("User does not have a mumble account")

    def update_groups(self, user):
        logger.debug("Updating %s groups for %s" % (self.name, user))
        if MumbleTasks.has_account(user):
            MumbleTasks.update_groups.delay(user.pk)

    def validate_user(self, user):
        if MumbleTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

    def update_all_groups(self):
        logger.debug("Updating all %s groups" % self.name)
        MumbleTasks.update_all_groups.delay()

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        urls = self.Urls()
        urls.auth_activate = 'mumble:activate'
        urls.auth_deactivate = 'mumble:deactivate'
        urls.auth_reset_password = 'mumble:reset_password'
        urls.auth_set_password = 'mumble:set_password'

        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'connect_url': request.user.mumble.username + '@' + self.service_url if MumbleTasks.has_account(request.user) else self.service_url,
            'username': request.user.mumble.username if MumbleTasks.has_account(request.user) else '',
        }, request=request)


@hooks.register('services_hook')
def register_mumble_service():
    return MumbleService()
