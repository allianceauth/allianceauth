import logging

from django.conf import settings
from django.template.loader import render_to_string

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook, MenuItemHook
from .tasks import OpenfireTasks
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class OpenfireService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'openfire'
        self.urlpatterns = urlpatterns
        self.service_url = settings.JABBER_URL
        self.access_perm = 'openfire.access_openfire'
        self.name_format = '{character_name}'

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
        urls.auth_activate = 'openfire:activate'
        urls.auth_deactivate = 'openfire:deactivate'
        urls.auth_set_password = 'openfire:set_password'
        urls.auth_reset_password = 'openfire:reset_password'
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
                              'fa fa-lock fa-fw fa-bullhorn',
                              'openfire:broadcast')

    def render(self, request):
        if request.user.has_perm('auth.jabber_broadcast') or request.user.has_perm('auth.jabber_broadcast_all'):
            return MenuItemHook.render(self, request)
        return ''


class FleetBroadcastFormatter(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              'Fleet Broadcast Formatter',
                              'fa fa-lock fa-fw fa-space-shuttle',
                              'services:fleet_format_tool')

    def render(self, request):
        if request.user.has_perm('auth.jabber_broadcast') or request.user.has_perm('auth.jabber_broadcast_all'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_formatter():
    return FleetBroadcastFormatter()


@hooks.register('menu_item_hook')
def register_menu():
    return JabberBroadcast()
