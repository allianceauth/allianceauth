import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from allianceauth.services.forms import ServicePasswordForm
from .manager import Ips4Manager
from .models import Ips4User
from .tasks import Ips4Tasks

logger = logging.getLogger(__name__)

ACCESS_PERM = 'ips4.access_ips4'


@login_required
@permission_required(ACCESS_PERM)
def activate_ips4(request):
    logger.debug("activate_ips4 called by user %s" % request.user)
    character = request.user.profile.main_character
    logger.debug("Adding IPS4 user for user %s with main character %s" % (request.user, character))
    result = Ips4Manager.add_user(Ips4Tasks.get_username(request.user), request.user.email)
    # if empty we failed
    if result[0] != "" and not Ips4Tasks.has_account(request.user):
        ips_user = Ips4User.objects.create(user=request.user, id=result[2], username=result[0])
        logger.debug("Updated authserviceinfo for user %s with IPS4 credentials." % request.user)
        # update_ips4_groups.delay(request.user.pk)
        logger.info("Successfully activated IPS4 for user %s" % request.user)
        messages.success(request, 'Activated IPSuite4 account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'services/service_credentials.html',
                      context={'credentials': credentials, 'service': 'IPSuite4'})
    else:
        logger.error("Unsuccessful attempt to activate IPS4 for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPSuite4 account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def reset_ips4_password(request):
    logger.debug("reset_ips4_password called by user %s" % request.user)
    if Ips4Tasks.has_account(request.user):
        result = Ips4Manager.update_user_password(request.user.ips4.username)
        # false we failed
        if result != "":
            logger.info("Successfully reset IPS4 password for user %s" % request.user)
            messages.success(request, 'Reset IPSuite4 password.')
            credentials = {
                'username': request.user.ips4.username,
                'password': result,
            }
            return render(request, 'services/service_credentials.html',
                          context={'credentials': credentials, 'service': 'IPSuite4'})

    logger.error("Unsuccessful attempt to reset IPS4 password for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your IPSuite4 account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def set_ips4_password(request):
    logger.debug("set_ips4_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid() and Ips4Tasks.has_account(request.user):
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            result = Ips4Manager.update_custom_password(request.user.ips4.username, plain_password=password)
            if result != "":
                logger.info("Successfully set IPS4 password for user %s" % request.user)
                messages.success(request, 'Set IPSuite4 password.')
            else:
                logger.error("Failed to install custom IPS4 password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your IPSuite4 account.')
            return redirect('services:services')
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'IPS4'}
    return render(request, 'services/service_password.html', context=context)


@login_required
@permission_required(ACCESS_PERM)
def deactivate_ips4(request):
    logger.debug("deactivate_ips4 called by user %s" % request.user)
    if Ips4Tasks.delete_user(request.user):
        logger.info("Successfully deactivated IPS4 for user %s" % request.user)
        messages.success(request, 'Deactivated IPSuite4 account.')
    else:
        logger.error("Unsuccessful attempt to deactivate IPS4 for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPSuite4 account.')
    return redirect("services:services")

