import logging

from django.template.loader import render_to_string
from django.conf import settings

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .tasks import DiscordTasks
from .urls import urlpatterns

logger = logging.getLogger(__name__)


class DiscordService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.urlpatterns = urlpatterns
        self.name = 'discord'
        self.service_ctrl_template = 'services/discord/discord_service_ctrl.html'
        self.access_perm = 'discord.access_discord'
        self.name_format = '{character_name}'

    def delete_user(self, user, notify_user=False):
        logger.debug('Deleting user %s %s account' % (user, self.name))
        return DiscordTasks.delete_user(user, notify_user=notify_user)

    def update_groups(self, user):
        logger.debug('Processing %s groups for %s' % (self.name, user))
        if DiscordTasks.has_account(user):
            DiscordTasks.update_groups.delay(user.pk)

    def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if DiscordTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

    def sync_nickname(self, user):
        logger.debug('Syncing %s nickname for user %s' % (self.name, user))
        DiscordTasks.update_nickname.delay(user.pk)

    def update_all_groups(self):
        logger.debug('Update all %s groups called' % self.name)
        DiscordTasks.update_all_groups.delay()

    def service_active_for_user(self, user):
        return user.has_perm(self.access_perm)

    def render_services_ctrl(self, request):
        return render_to_string(self.service_ctrl_template, {
            'discord_uid': request.user.discord.uid if DiscordTasks.has_account(request.user) else None,
            'DISCORD_SERVER_ID': getattr(settings, 'DISCORD_GUILD_ID', ''),
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return DiscordService()
