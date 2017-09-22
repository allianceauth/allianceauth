import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from allianceauth.services.forms import ServicePasswordForm

from .manager import MumbleManager
from .tasks import MumbleTasks

logger = logging.getLogger(__name__)

ACCESS_PERM = 'mumble.access_mumble'


@login_required
@permission_required(ACCESS_PERM)
def activate_mumble(request):
    logger.debug("activate_mumble called by user %s" % request.user)
    character = request.user.profile.main_character
    ticker = character.corporation_ticker

    logger.debug("Adding mumble user for %s with main character %s" % (request.user, character))
    result = MumbleManager.create_user(request.user, ticker, character.character_name)

    if result:
        logger.debug("Updated authserviceinfo for user %s with mumble credentials. Updating groups." % request.user)
        MumbleTasks.update_groups.apply(args=(request.user.pk,))  # Run synchronously to prevent timing issues
        logger.info("Successfully activated mumble for user %s" % request.user)
        messages.success(request, 'Activated Mumble account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'services/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Mumble'})
    else:
        logger.error("Unsuccessful attempt to activate mumble for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Mumble account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def deactivate_mumble(request):
    logger.debug("deactivate_mumble called by user %s" % request.user)
    # if we successfully remove the user or the user is already removed
    if MumbleManager.delete_user(request.user):
        logger.info("Successfully deactivated mumble for user %s" % request.user)
        messages.success(request, 'Deactivated Mumble account.')
    else:
        logger.error("Unsuccessful attempt to deactivate mumble for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Mumble account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def reset_mumble_password(request):
    logger.debug("reset_mumble_password called by user %s" % request.user)
    result = MumbleManager.update_user_password(request.user)

    # if blank we failed
    if result != "":
        logger.info("Successfully reset mumble password for user %s" % request.user)
        messages.success(request, 'Reset Mumble password.')
        credentials = {
            'username': request.user.mumble.username,
            'password': result,
        }
        return render(request, 'services/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Mumble'})
    else:
        logger.error("Unsuccessful attempt to reset mumble password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Mumble account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def set_mumble_password(request):
    logger.debug("set_mumble_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid() and MumbleTasks.has_account(request.user):
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            result = MumbleManager.update_user_password(request.user, password=password)
            if result != "":
                logger.info("Successfully reset mumble password for user %s" % request.user)
                messages.success(request, 'Set Mumble password.')
            else:
                logger.error("Failed to install custom mumble password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your Mumble account.')
            return redirect("services:services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Mumble'}
    return render(request, 'services/service_password.html', context=context)
