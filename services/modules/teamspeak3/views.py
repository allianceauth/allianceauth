import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from authentication.states import BLUE_STATE
from authentication.models import AuthServicesInfo
from eveonline.managers import EveManager
from eveonline.models import EveAllianceInfo

from services.modules.teamspeak3.manager import Teamspeak3Manager

from .forms import TeamspeakJoinForm
from .tasks import Teamspeak3Tasks
from .models import Teamspeak3User

logger = logging.getLogger(__name__)

ACCESS_PERM = 'teamspeak3.access_teamspeak3'


@login_required
@permission_required(ACCESS_PERM)
def activate_teamspeak3(request):
    logger.debug("activate_teamspeak3 called by user %s" % request.user)

    authinfo = AuthServicesInfo.objects.get(user=request.user)
    character = EveManager.get_main_character(request.user)
    ticker = character.corporation_ticker
    with Teamspeak3Manager() as ts3man:
        if authinfo.state == BLUE_STATE:
            logger.debug("Adding TS3 user for blue user %s with main character %s" % (request.user, character))
            # Blue members should have alliance ticker (if in alliance)
            if EveAllianceInfo.objects.filter(alliance_id=character.alliance_id).exists():
                alliance = EveAllianceInfo.objects.filter(alliance_id=character.alliance_id)[0]
                ticker = alliance.alliance_ticker
            result = ts3man.add_blue_user(character.character_name, ticker)
        else:
            logger.debug("Adding TS3 user for user %s with main character %s" % (request.user, character))
            result = ts3man.add_user(character.character_name, ticker)

    # if its empty we failed
    if result[0] is not "":
        Teamspeak3User.objects.update_or_create(user=request.user, defaults={'uid': result[0], 'perm_key': result[1]})
        logger.debug("Updated authserviceinfo for user %s with TS3 credentials. Updating groups." % request.user)
        logger.info("Successfully activated TS3 for user %s" % request.user)
        messages.success(request, 'Activated TeamSpeak3 account.')
        return redirect("auth_verify_teamspeak3")
    logger.error("Unsuccessful attempt to activate TS3 for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your TeamSpeak3 account.')
    return redirect("auth_services")


@login_required
@permission_required(ACCESS_PERM)
def verify_teamspeak3(request):
    logger.debug("verify_teamspeak3 called by user %s" % request.user)
    if not Teamspeak3Tasks.has_account(request.user):
        logger.warn("Unable to validate user %s teamspeak: no teamspeak data" % request.user)
        return redirect("auth_services")
    if request.method == "POST":
        form = TeamspeakJoinForm(request.POST)
        if form.is_valid():
            Teamspeak3Tasks.update_groups.delay(request.user.pk)
            logger.debug("Validated user %s joined TS server" % request.user)
            return redirect("auth_services")
    else:
        form = TeamspeakJoinForm({'username': request.user.teamspeak3.uid})
    context = {
        'form': form,
        'authinfo': {'teamspeak3_uid': request.user.teamspeak3.uid,
                     'teamspeak3_perm_key': request.user.teamspeak3.perm_key},
    }
    return render(request, 'registered/teamspeakjoin.html', context=context)


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
    return redirect("auth_services")


@login_required
@permission_required(ACCESS_PERM)
def reset_teamspeak3_perm(request):
    logger.debug("reset_teamspeak3_perm called by user %s" % request.user)
    if not Teamspeak3Tasks.has_account(request.user):
        return redirect("auth_services")
    authinfo = AuthServicesInfo.objects.get(user=request.user)
    character = EveManager.get_main_character(request.user)
    logger.debug("Deleting TS3 user for user %s" % request.user)
    with Teamspeak3Manager() as ts3man:
        ts3man.delete_user(request.user.teamspeak3.uid)

        if authinfo.state == BLUE_STATE:
            logger.debug(
                "Generating new permission key for blue user %s with main character %s" % (request.user, character))
            result = ts3man.generate_new_blue_permissionkey(request.user.teamspeak3.uid,
                                                            character.character_name,
                                                            character.corporation_ticker)
        else:
            logger.debug("Generating new permission key for user %s with main character %s" % (request.user, character))
            result = ts3man.generate_new_permissionkey(request.user.teamspeak3.uid, character.character_name,
                                                       character.corporation_ticker)

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
    return redirect("auth_services")
