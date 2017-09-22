import logging

from django.conf import settings
from django.template.loader import render_to_string

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import MarketTasks
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class MarketService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'market'
        self.urlpatterns = urlpatterns
        self.service_url = settings.MARKET_URL
        self.access_perm = 'market.access_market'

    @property
    def title(self):
        return "Alliance Market"

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return MarketTasks.delete_user(user, notify_user=notify_user)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if MarketTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user)

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        urls = self.Urls()
        urls.auth_activate = 'evernusmarket:activate'
        urls.auth_deactivate = 'evernusmarket:deactivate'
        urls.auth_reset_password = 'evernusmarket:reset_password'
        urls.auth_set_password = 'evernusmarket:set_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.market.username if MarketTasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return MarketService()
