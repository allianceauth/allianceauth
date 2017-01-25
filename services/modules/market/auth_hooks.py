from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import render_to_string

from services.hooks import ServicesHook
from alliance_auth import hooks

from .urls import urlpatterns
from .tasks import MarketTasks

import logging

logger = logging.getLogger(__name__)


class MarketService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.name = 'market'
        self.urlpatterns = urlpatterns
        self.service_url = settings.MARKET_URL

    @property
    def title(self):
        return "Alliance Market"

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return MarketTasks.delete_user(user, notify_user=notify_user)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if MarketTasks.has_account(user) and self.service_active_for_user(user):
            self.delete_user(user)

    def service_enabled_members(self):
        return settings.ENABLE_AUTH_MARKET or False

    def service_enabled_blues(self):
        return settings.ENABLE_BLUE_MARKET or False

    def render_services_ctrl(self, request):
        urls = self.Urls()
        urls.auth_activate = 'auth_activate_market'
        urls.auth_deactivate = 'auth_deactivate_market'
        urls.auth_reset_password = 'auth_reset_market_password'
        urls.auth_set_password = 'auth_set_market_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': request.user.market.username if MarketTasks.has_account(request.user) else ''
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return MarketService()
