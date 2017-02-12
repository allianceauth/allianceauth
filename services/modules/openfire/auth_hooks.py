from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import render_to_string

from services.hooks import ServicesHook, MenuItemHook
from alliance_auth import hooks

from .urls import urlpatterns
from .tasks import OpenfireTasks

import logging

logger = logging.getLogger(__name__)


class OpenfireService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'openfire'
        self.urlpatterns = urlpatterns
        self.service_url = settings.JABBER_URL
        self.access_perm = 'openfire.access_openfire'

    @property
    def title(self):
        return "Jabber"

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return OpenfireTasks.delete_user(user, notify_user=notify_user)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if OpenfireTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

    def update_groups(self, user):
        logger.debug('Updating %s groups for %s' % (self.name, user))
        if OpenfireTasks.has_account(user):
            OpenfireTasks.update_groups.delay(user.pk)

    def update_all_groups(self):
        logger.debug('Update all %s groups called' % self.name)
        OpenfireTasks.update_all_groups.delay()

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
        urls.auth_activate = 'auth_activate_openfire'
        urls.auth_deactivate = 'auth_deactivate_openfire'
        urls.auth_set_password = 'auth_set_openfire_password'
        urls.auth_reset_password = 'auth_reset_openfire_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.openfire.username if OpenfireTasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return OpenfireService()


class JabberBroadcast(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              'Jabber Broadcast',
                              'fa fa-lock fa-fw fa-bullhorn grayiconecolor',
                              'auth_jabber_broadcast_view')

    def render(self, request):
        if request.user.has_perm('auth.jabber_broadcast'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_util_hook')
def register_menu():
    return JabberBroadcast()
