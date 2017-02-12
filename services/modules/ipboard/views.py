from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from services.forms import ServicePasswordForm
from eveonline.managers import EveManager

from .manager import IPBoardManager
from .tasks import IpboardTasks
from .models import IpboardUser

import logging

logger = logging.getLogger(__name__)

ACCESS_PERM = 'ipboard.access_ipboard'


@login_required
@permission_required(ACCESS_PERM)
def activate_ipboard_forum(request):
    logger.debug("activate_ipboard_forum called by user %s" % request.user)
    character = EveManager.get_main_character(request.user)
    logger.debug("Adding ipboard user for user %s with main character %s" % (request.user, character))
    result = IPBoardManager.add_user(character.character_name, request.user.email)
    if result[0] != "":
        ipboard_user = IpboardUser()
        ipboard_user.user = request.user
        ipboard_user.username = result[0]
        ipboard_user.save()
        logger.debug("Updated authserviceinfo for user %s with ipboard credentials. Updating groups." % request.user)
        IpboardTasks.update_groups.delay(request.user.pk)
        logger.info("Successfully activated ipboard for user %s" % request.user)
        messages.success(request, 'Activated IPBoard account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'IPBoard'})
    else:
        logger.error("Unsuccessful attempt to activate ipboard for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPBoard account.')
    return redirect("auth_services")


@login_required
@permission_required(ACCESS_PERM)
def deactivate_ipboard_forum(request):
    logger.debug("deactivate_ipboard_forum called by user %s" % request.user)
    # false we failed
    if IpboardTasks.delete_user(request.user):
        logger.info("Successfully deactivated ipboard for user %s" % request.user)
        messages.success(request, 'Deactivated IPBoard account.')
    else:
        logger.error("Unsuccessful attempt to deactviate ipboard for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPBoard account.')
    return redirect("auth_services")


@login_required
@permission_required(ACCESS_PERM)
def set_ipboard_password(request):
    logger.debug("set_ipboard_password called by user %s" % request.user)
    error = None
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid() and IpboardTasks.has_account(request.user):
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            result = IPBoardManager.update_user_password(request.user.ipboard.username, request.user.email,
                                                         plain_password=password)
            if result != "":
                logger.info("Successfully set IPBoard password for user %s" % request.user)
                messages.success(request, 'Set IPBoard password.')
            else:
                logger.error("Failed to install custom ipboard password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your IPBoard account.')
            return redirect("auth_services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'IPBoard', 'error': error}
    return render(request, 'registered/service_password.html', context=context)


@login_required
@permission_required(ACCESS_PERM)
def reset_ipboard_password(request):
    logger.debug("reset_ipboard_password called by user %s" % request.user)
    if IpboardTasks.has_account(request.user):
        result = IPBoardManager.update_user_password(request.user.ipboard.username, request.user.email)
        if result != "":
            logger.info("Successfully reset ipboard password for user %s" % request.user)
            messages.success(request, 'Reset IPBoard password.')
            credentials = {
                'username': request.user.ipboard.username,
                'password': result,
            }
            return render(request, 'registered/service_credentials.html',
                          context={'credentials': credentials, 'service': 'IPBoard'})

    logger.error("Unsuccessful attempt to reset ipboard password for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your IPBoard account.')
    return redirect("auth_services")
