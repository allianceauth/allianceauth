from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

from .manager import SeatManager

from eveonline.managers import EveManager

from .tasks import SeatTasks
from .models import SeatUser
from services.forms import ServicePasswordForm

import logging

logger = logging.getLogger(__name__)

ACCESS_PERM = 'seat.access_seat'


@login_required
@permission_required(ACCESS_PERM)
def activate_seat(request):
    logger.debug("activate_seat called by user %s" % request.user)
    # Valid now we get the main characters
    character = EveManager.get_main_character(request.user)
    logger.debug("Checking SeAT for inactive users with the same username")
    stat = SeatManager.check_user_status(character.character_name)
    if stat == {}:
        logger.debug("User not found, adding SeAT user for user %s with main character %s" % (request.user, character))
        result = SeatManager.add_user(character.character_name, request.user.email)
    else:
        logger.debug("User found, resetting password")
        username = SeatManager.enable_user(stat["name"])
        password = SeatManager.update_user_password(username, request.user.email)
        result = [username, password]
    # if empty we failed
    if result[0] and result[1]:
        SeatUser.objects.update_or_create(user=request.user, defaults={'username': result[0]})
        logger.debug("Updated SeatUser for user %s with SeAT credentials. Adding eve-apis..." % request.user)
        SeatTasks.update_roles.delay(request.user.pk)
        logger.info("Successfully activated SeAT for user %s" % request.user)
        SeatManager.synchronize_eveapis(request.user)
        credentials = {
            'username': request.user.seat.username,
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'SeAT'})
    logger.error("Unsuccessful attempt to activate seat for user %s" % request.user)
    return redirect("auth_services")


@login_required
@permission_required(ACCESS_PERM)
def deactivate_seat(request):
    logger.debug("deactivate_seat called by user %s" % request.user)
    # false we failed
    if SeatTasks.delete_user(request.user):
        logger.info("Successfully deactivated SeAT for user %s" % request.user)
        return redirect("auth_services")
    else:
        logging.error("User does not have a SeAT account")
    logger.error("Unsuccessful attempt to activate SeAT for user %s" % request.user)
    return redirect("auth_services")


@login_required
@permission_required(ACCESS_PERM)
def reset_seat_password(request):
    logger.debug("reset_seat_password called by user %s" % request.user)
    if SeatTasks.has_account(request.user):
        result = SeatManager.update_user_password(request.user.seat.username, request.user.email)
        # false we failed
        if result:
            credentials = {
                'username': request.user.seat.username,
                'password': result,
            }
            logger.info("Succesfully reset SeAT password for user %s" % request.user)
            return render(request, 'registered/service_credentials.html',
                          context={'credentials': credentials, 'service': 'SeAT'})
    logger.error("Unsuccessful attempt to reset SeAT password for user %s" % request.user)
    return redirect("auth_services")


@login_required
@permission_required(ACCESS_PERM)
def set_seat_password(request):
    logger.debug("set_seat_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid() and SeatTasks.has_account(request.user):
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            result = SeatManager.update_user_password(request.user.seat.username,
                                                      request.user.email,
                                                      plain_password=password)
            if result:
                logger.info("Succesfully reset SeAT password for user %s" % request.user)
                return redirect("auth_services")
            else:
                logger.error("Failed to install custom SeAT password for user %s" % request.user)
        else:
            logger.error("Invalid SeAT password provided")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()
    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'SeAT'}
    return render(request, 'registered/service_password.html', context)
