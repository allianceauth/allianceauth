import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from allianceauth.services.forms import ServicePasswordForm
from .manager import SeatManager
from .models import SeatUser
from .tasks import SeatTasks

logger = logging.getLogger(__name__)

ACCESS_PERM = 'seat.access_seat'
SERVICE_NAME = {'service': 'SeAT'}


@login_required
@permission_required(ACCESS_PERM)
def activate_seat(request):
    logger.debug("activate_seat called by user %s" % request.user)
    character = request.user.profile.main_character
    logger.debug("Checking SeAT for inactive users with the same username")
    stat = SeatManager.check_user_status(character.character_name)
    if stat == {}:
        logger.debug("User not found, adding SeAT user for user %s with main character %s" % (request.user, character))
        result = SeatManager.add_user(SeatTasks.get_username(request.user), request.user.email)
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
        messages.add_message(request, messages.SUCCESS, _('Successfully activated your %(service)s account.') %
                             SERVICE_NAME)
        credentials = {
            'username': request.user.seat.username,
            'password': result[1],
        }
        return render(request, 'services/service_credentials.html',
                      context={'credentials': credentials, 'service': 'SeAT'})
    messages.add_message(request, messages.ERROR,
                         _('Failed to activate your %(service)s account, please contact your administrator.') %
                         SERVICE_NAME)
    logger.error("Unsuccessful attempt to activate seat for user %s" % request.user)
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def deactivate_seat(request):
    logger.debug("deactivate_seat called by user %s" % request.user)
    # false we failed
    if SeatTasks.delete_user(request.user):
        messages.add_message(request, messages.SUCCESS,
                             _('Successfully deactivated your %(service)s account.') % SERVICE_NAME)
        logger.info("Successfully deactivated SeAT for user %s" % request.user)
        return redirect("services:services")
    else:
        logging.error("User does not have a SeAT account")
    messages.add_message(request, messages.ERROR,
                         _('Failed to deactivate your %(service)s account, please contact your administrator.') %
                         SERVICE_NAME)
    logger.error("Unsuccessful attempt to activate SeAT for user %s" % request.user)
    return redirect("services:services")


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
            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully reset your %(service)s password.') % {'service': 'SeAT'})
            logger.info("Succesfully reset SeAT password for user %s" % request.user)
            return render(request, 'services/service_credentials.html',
                          context={'credentials': credentials, 'service': 'SeAT'})
    logger.error("Unsuccessful attempt to reset SeAT password for user %s" % request.user)
    messages.add_message(request, messages.ERROR,
                         _('Failed to reset your %(service)s password, please contact your administrator.') %
                         {'service': 'SeAT'})
    return redirect("services:services")


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
                messages.add_message(request, messages.SUCCESS,
                                     _('Successfully set your %(service)s password.') % SERVICE_NAME)
                logger.info("Succesfully reset SeAT password for user %s" % request.user)
                return redirect("services:services")
            else:
                messages.add_message(request, messages.ERROR,
                                     _('Failed to set your %(service)s password, please contact your administrator.') %
                                     SERVICE_NAME)
                logger.error("Failed to install custom SeAT password for user %s" % request.user)
        else:
            messages.add_message(request, messages.ERROR, _('Invalid password.'))
            logger.error("Invalid SeAT password provided")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()
    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'SeAT'}
    return render(request, 'services/service_password.html', context)
