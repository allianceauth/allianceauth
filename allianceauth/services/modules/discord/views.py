import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

from allianceauth.services.views import superuser_test
from .manager import DiscordOAuthManager
from .tasks import DiscordTasks

logger = logging.getLogger(__name__)

ACCESS_PERM = 'discord.access_discord'


@login_required
@permission_required(ACCESS_PERM)
def deactivate_discord(request):
    logger.debug("deactivate_discord called by user %s" % request.user)
    if DiscordTasks.delete_user(request.user):
        logger.info("Successfully deactivated discord for user %s" % request.user)
        messages.success(request, 'Deactivated Discord account.')
    else:
        logger.error("Unsuccessful attempt to deactivate discord for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Discord account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def reset_discord(request):
    logger.debug("reset_discord called by user %s" % request.user)
    if DiscordTasks.delete_user(request.user):
        logger.info("Successfully deleted discord user for user %s - forwarding to discord activation." % request.user)
        return redirect("discord:activate")
    logger.error("Unsuccessful attempt to reset discord for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your Discord account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def activate_discord(request):
    logger.debug("activate_discord called by user %s" % request.user)
    return redirect(DiscordOAuthManager.generate_oauth_redirect_url())


@login_required
@permission_required(ACCESS_PERM)
def discord_callback(request):
    logger.debug("Received Discord callback for activation of user %s" % request.user)
    code = request.GET.get('code', None)
    if not code:
        logger.warn("Did not receive OAuth code from callback of user %s" % request.user)
        return redirect("services:services")
    if DiscordTasks.add_user(request.user, code):
        logger.info("Successfully activated Discord for user %s" % request.user)
        messages.success(request, 'Activated Discord account.')
    else:
        logger.error("Failed to activate Discord for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Discord account.')
    return redirect("services:services")


@login_required
@user_passes_test(superuser_test)
def discord_add_bot(request):
    return redirect(DiscordOAuthManager.generate_bot_add_url())
