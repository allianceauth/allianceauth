import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from allianceauth.services.forms import ServicePasswordForm
from .manager import MarketManager
from .models import MarketUser
from .tasks import MarketTasks

logger = logging.getLogger(__name__)

ACCESS_PERM = 'market.access_market'


@login_required
@permission_required(ACCESS_PERM)
def activate_market(request):
    logger.debug("activate_market called by user %s" % request.user)
    character = request.user.profile.main_character
    if character is not None:
        logger.debug("Adding market user for user %s with main character %s" % (request.user, character))
        result = MarketManager.add_user(character.character_name, request.user.email, character.character_id,
                                        character.character_name)
        # if empty we failed
        if result[0] != "":
            MarketUser.objects.create(user=request.user, username=result[0])
            logger.debug("Updated authserviceinfo for user %s with market credentials." % request.user)
            logger.info("Successfully activated market for user %s" % request.user)
            messages.success(request, 'Activated Alliance Market account.')
            credentials = {
                'username': result[0],
                'password': result[1],
            }
            return render(request, 'services/service_credentials.html',
                          context={'credentials': credentials, 'service': 'Alliance Market'})
    logger.error("Unsuccessful attempt to activate market for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your Alliance Market account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def deactivate_market(request):
    logger.debug("deactivate_market called by user %s" % request.user)
    # false we failed
    if MarketTasks.delete_user(request.user):
        logger.info("Successfully deactivated market for user %s" % request.user)
        messages.success(request, 'Deactivated Alliance Market account.')
    else:
        logger.error("Unsuccessful attempt to activate market for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Alliance Market account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def reset_market_password(request):
    logger.debug("reset_market_password called by user %s" % request.user)
    if MarketTasks.has_account(request.user):
        result = MarketManager.update_user_password(request.user.market.username)
        # false we failed
        if result != "":
            logger.info("Successfully reset market password for user %s" % request.user)
            messages.success(request, 'Reset Alliance Market password.')
            credentials = {
                'username': request.user.market.username,
                'password': result,
            }
            return render(request, 'services/service_credentials.html',
                          context={'credentials': credentials, 'service': 'Alliance Market'})

    logger.error("Unsuccessful attempt to reset market password for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your Alliance Market account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def set_market_password(request):
    logger.debug("set_market_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid() and MarketTasks.has_account(request.user):
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            result = MarketManager.update_custom_password(request.user.market.username, password)
            if result != "":
                logger.info("Successfully reset market password for user %s" % request.user)
                messages.success(request, 'Set Alliance Market password.')
            else:
                logger.error("Failed to install custom market password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your Alliance Market account.')
            return redirect("services:services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Market'}
    return render(request, 'services/service_password.html', context=context)
