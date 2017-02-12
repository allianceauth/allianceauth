from __future__ import unicode_literals
from django.template.loader import render_to_string
from django.conf import settings
from notifications import notify

from alliance_auth import hooks
from services.hooks import ServicesHook
from .tasks import MumbleTasks
from .manager import MumbleManager
from .urls import urlpatterns

import logging

logger = logging.getLogger(__name__)


class MumbleService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'mumble'
        self.urlpatterns = urlpatterns
        self.service_url = settings.MUMBLE_URL
        self.access_perm = 'mumble.access_mumble'

    def delete_user(self, user, notify_user=False):
        logging.debug("Deleting user %s %s account" % (user, self.name))
        if MumbleManager.delete_user(user):
            if notify_user:
                notify(user, 'Mumble Account Disabled', level='danger')
            return True
        return False

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
        urls.auth_activate = 'auth_activate_mumble'
        urls.auth_deactivate = 'auth_deactivate_mumble'
        urls.auth_reset_password = 'auth_reset_mumble_password'
        urls.auth_set_password = 'auth_set_mumble_password'

        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.mumble.username if MumbleTasks.has_account(request.user) else '',
        }, request=request)


@hooks.register('services_hook')
def register_mumble_service():
    return MumbleService()
