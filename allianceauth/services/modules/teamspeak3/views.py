import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.conf import settings
from .manager import Teamspeak3Manager
from .forms import TeamspeakJoinForm
from .models import Teamspeak3User
from .tasks import Teamspeak3Tasks

logger = logging.getLogger(__name__)

ACCESS_PERM = 'teamspeak3.access_teamspeak3'


@login_required
@permission_required(ACCESS_PERM)
def activate_teamspeak3(request):
    logger.debug("activate_teamspeak3 called by user %s" % request.user)

    character = request.user.profile.main_character
    with Teamspeak3Manager() as ts3man:
        logger.debug("Adding TS3 user for user %s with main character %s" % (request.user, character))
        result = ts3man.add_user(request.user, Teamspeak3Tasks.get_username(request.user))

    # if its empty we failed
    if result[0] is not "":
        Teamspeak3User.objects.update_or_create(user=request.user, defaults={'uid': result[0], 'perm_key': result[1]})
        logger.debug("Updated authserviceinfo for user %s with TS3 credentials. Updating groups." % request.user)
        logger.info("Successfully activated TS3 for user %s" % request.user)
        messages.success(request, 'Activated TeamSpeak3 account.')
        return redirect("teamspeak3:verify")
    logger.error("Unsuccessful attempt to activate TS3 for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your TeamSpeak3 account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def verify_teamspeak3(request):
    logger.debug("verify_teamspeak3 called by user %s" % request.user)
    if not Teamspeak3Tasks.has_account(request.user):
        logger.warn("Unable to validate user %s teamspeak: no teamspeak data" % request.user)
        return redirect("services:services")
    if request.method == "POST":
        form = TeamspeakJoinForm(request.POST)
        if form.is_valid():
            Teamspeak3Tasks.update_groups.delay(request.user.pk)
            logger.debug("Validated user %s joined TS server" % request.user)
            return redirect("services:services")
    else:
        form = TeamspeakJoinForm(initial={'username': request.user.teamspeak3.uid})
    context = {
        'form': form,
        'authinfo': {'teamspeak3_uid': request.user.teamspeak3.uid,
                     'teamspeak3_perm_key': request.user.teamspeak3.perm_key},
        'public_url': settings.TEAMSPEAK3_PUBLIC_URL,
    }
    return render(request, 'services/teamspeak3/teamspeakjoin.html', context=context)


@login_required
@permission_required(ACCESS_PERM)
def deactivate_teamspeak3(request):
    logger.debug("deactivate_teamspeak3 called by user %s" % request.user)
    if Teamspeak3Tasks.has_account(request.user) and Teamspeak3Tasks.delete_user(request.user):
        logger.info("Successfully deactivated TS3 for user %s" % request.user)
        messages.success(request, 'Deactivated TeamSpeak3 account.')
    else:
        logger.error("Unsuccessful attempt to deactivate TS3 for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your TeamSpeak3 account.')
    return redirect("services:services")


@login_required
@permission_required(ACCESS_PERM)
def reset_teamspeak3_perm(request):
    logger.debug("reset_teamspeak3_perm called by user %s" % request.user)
    if not Teamspeak3Tasks.has_account(request.user):
        return redirect("services:services")
    logger.debug("Deleting TS3 user for user %s" % request.user)
    with Teamspeak3Manager() as ts3man:
        ts3man.delete_user(request.user.teamspeak3.uid)

        logger.debug("Generating new permission key for user %s" % request.user)
        result = ts3man.generate_new_permissionkey(request.user.teamspeak3.uid, request.user, Teamspeak3Tasks.get_username(request.user))

    # if blank we failed
    if result[0] != "":
        Teamspeak3User.objects.update_or_create(user=request.user, defaults={'uid': result[0], 'perm_key': result[1]})
        logger.debug("Updated authserviceinfo for user %s with TS3 credentials. Updating groups." % request.user)
        Teamspeak3Tasks.update_groups.delay(request.user.pk)
        logger.info("Successfully reset TS3 permission key for user %s" % request.user)
        messages.success(request, 'Reset TeamSpeak3 permission key.')
    else:
        logger.error("Unsuccessful attempt to reset TS3 permission key for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your TeamSpeak3 account.')
    return redirect("services:services")
