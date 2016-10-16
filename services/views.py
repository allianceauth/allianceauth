from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib import messages
from eveonline.models import EveCharacter
from eveonline.models import EveAllianceInfo
from authentication.models import AuthServicesInfo
from services.managers.openfire_manager import OpenfireManager
from services.managers.phpbb3_manager import Phpbb3Manager
from services.managers.mumble_manager import MumbleManager
from services.managers.ipboard_manager import IPBoardManager
from services.managers.xenforo_manager import XenForoManager
from services.managers.teamspeak3_manager import Teamspeak3Manager
from services.managers.discord_manager import DiscordOAuthManager
from services.managers.discourse_manager import DiscourseManager
from services.managers.ips4_manager import Ips4Manager
from services.managers.smf_manager import smfManager
from services.managers.market_manager import marketManager
from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager
from services.tasks import update_jabber_groups
from services.tasks import update_mumble_groups
from services.tasks import update_forum_groups
from services.tasks import update_ipboard_groups
from services.tasks import update_smf_groups
from services.tasks import update_teamspeak3_groups
from services.tasks import update_discord_groups
from services.tasks import update_discord_nickname
from services.tasks import update_discourse_groups
from services.forms import JabberBroadcastForm
from services.forms import FleetFormatterForm
from services.forms import ServicePasswordForm
from services.forms import TeamspeakJoinForm
from authentication.decorators import members_and_blues
from authentication.states import MEMBER_STATE, BLUE_STATE

import datetime

import logging

logger = logging.getLogger(__name__)


@login_required
def fleet_formatter_view(request):
    logger.debug("fleet_formatter_view called by user %s" % request.user)
    generated = ""
    if request.method == 'POST':
        form = FleetFormatterForm(request.POST)
        logger.debug("Received POST request containing form, valid: %s" % form.is_valid())
        if form.is_valid():
            generated = "Fleet Name: " + form.cleaned_data['fleet_name'] + "\n"
            generated = generated + "FC: " + form.cleaned_data['fleet_commander'] + "\n"
            generated = generated + "Comms: " + form.cleaned_data['fleet_comms'] + "\n"
            generated = generated + "Fleet Type: " + form.cleaned_data['fleet_type'] + " || " + form.cleaned_data[
                'ship_priorities'] + "\n"
            generated = generated + "Form Up: " + form.cleaned_data['formup_location'] + " @ " + form.cleaned_data[
                'formup_time'] + "\n"
            generated = generated + "Duration: " + form.cleaned_data['expected_duration'] + "\n"
            generated = generated + "Reimbursable: " + form.cleaned_data['reimbursable'] + "\n"
            generated = generated + "Important: " + form.cleaned_data['important'] + "\n"
            if form.cleaned_data['comments'] != "":
                generated = generated + "Why: " + form.cleaned_data['comments'] + "\n"
            logger.info("Formatted fleet broadcast for user %s" % request.user)
    else:
        form = FleetFormatterForm()
        logger.debug("Returning empty form to user %s" % request.user)

    context = {'form': form, 'generated': generated}

    return render(request, 'registered/fleetformattertool.html', context=context)


@login_required
@permission_required('auth.jabber_broadcast')
def jabber_broadcast_view(request):
    logger.debug("jabber_broadcast_view called by user %s" % request.user)
    allchoices = []
    if request.user.has_perm('auth.jabber_broadcast_all'):
        allchoices.append(('all', 'all'))
        for g in Group.objects.all():
            allchoices.append((str(g.name), str(g.name)))
    else:
        for g in request.user.groups.all():
            allchoices.append((str(g.name), str(g.name)))
    if request.method == 'POST':
        form = JabberBroadcastForm(request.POST)
        form.fields['group'].choices = allchoices
        logger.debug("Received POST request containing form, valid: %s" % form.is_valid())
        if form.is_valid():
            user_info = AuthServicesInfo.objects.get(user=request.user)
            main_char = EveCharacter.objects.get(character_id=user_info.main_char_id)
            logger.debug("Processing jabber broadcast for user %s with main character %s" % (user_info, main_char))
            if user_info.main_char_id != "":
                message_to_send = form.cleaned_data[
                                      'message'] + "\n##### SENT BY: " + "[" + main_char.corporation_ticker + "]" + \
                                  main_char.character_name + " TO: " + \
                                  form.cleaned_data['group'] + " WHEN: " + datetime.datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M:%S") + " #####\n##### Replies are NOT monitored #####\n"
                group_to_send = form.cleaned_data['group']

                OpenfireManager.send_broadcast_threaded(group_to_send, message_to_send, )

            else:
                message_to_send = form.cleaned_data[
                    'message'] + "\n##### SENT BY: " + "No character but can send pings?" + " TO: " + \
                    form.cleaned_data['group'] + " WHEN: " + datetime.datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M:%S") + " #####\n##### Replies are NOT monitored #####\n"
                group_to_send = form.cleaned_data['group']

                OpenfireManager.send_broadcast_threaded(group_to_send, message_to_send, )

            messages.success(request, 'Sent jabber broadcast to %s' % group_to_send)
            logger.info("Sent jabber broadcast on behalf of user %s" % request.user)
    else:
        form = JabberBroadcastForm()
        form.fields['group'].choices = allchoices
        logger.debug("Generated broadcast form for user %s containing %s groups" % (
            request.user, len(form.fields['group'].choices)))

    context = {'form': form}
    return render(request, 'registered/jabberbroadcast.html', context=context)


@login_required
@members_and_blues()
def services_view(request):
    logger.debug("services_view called by user %s" % request.user)
    auth = AuthServicesInfo.objects.get_or_create(user=request.user)[0]

    services = [
        'FORUM',
        'JABBER',
        'MUMBLE',
        'IPBOARD',
        'TEAMSPEAK3',
        'DISCORD',
        'DISCOURSE',
        'IPS4',
        'SMF',
        'MARKET',
        'XENFORO',
    ]

    context = {'authinfo': auth}

    for s in services:
        context['SHOW_' + s] = (getattr(settings, 'ENABLE_AUTH_' + s) and (
            auth.state == MEMBER_STATE or request.user.is_superuser)) or (getattr(settings, 'ENABLE_BLUE_' + s) and (
                auth.state == BLUE_STATE or request.user.is_superuser))

    return render(request, 'registered/services.html', context=context)


def superuser_test(user):
    return user.is_superuser


@login_required
@members_and_blues()
def activate_forum(request):
    logger.debug("activate_forum called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding phpbb user for user %s with main character %s" % (request.user, character))
    result = Phpbb3Manager.add_user(character.character_name, request.user.email, ['REGISTERED'], authinfo.main_char_id)
    # if empty we failed
    if result[0] != "":
        AuthServicesInfoManager.update_user_forum_info(result[0], request.user)
        logger.debug("Updated authserviceinfo for user %s with forum credentials. Updating groups." % request.user)
        update_forum_groups.delay(request.user.pk)
        logger.info("Successfully activated forum for user %s" % request.user)
        messages.success(request, 'Activated forum account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Forum'})
    else:
        logger.error("Unsuccessful attempt to activate forum for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your forum account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_forum(request):
    logger.debug("deactivate_forum called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = Phpbb3Manager.disable_user(authinfo.forum_username)
    # false we failed
    if result:
        AuthServicesInfoManager.update_user_forum_info("", request.user)
        logger.info("Successfully deactivated forum for user %s" % request.user)
        messages.success(request, 'Deactivated forum account.')
    else:
        logger.error("Unsuccessful attempt to activate forum for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your forum account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_forum_password(request):
    logger.debug("reset_forum_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = Phpbb3Manager.update_user_password(authinfo.forum_username, authinfo.main_char_id)
    # false we failed
    if result != "":
        logger.info("Successfully reset forum password for user %s" % request.user)
        messages.success(request, 'Reset forum password.')
        credentials = {
            'username': authinfo.forum_username,
            'password': result,
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Forum'})
    else:
        logger.error("Unsuccessful attempt to reset forum password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your forum account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def activate_xenforo_forum(request):
    logger.debug("activate_xenforo_forum called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding XenForo user for user %s with main character %s" % (request.user, character))
    result = XenForoManager.add_user(character.character_name, request.user.email)
    # Based on XenAPI's response codes
    if result['response']['status_code'] == 200:
        logger.info("Updated authserviceinfo for user %s with XenForo credentials. Updating groups." % request.user)
        AuthServicesInfoManager.update_user_xenforo_info(result['username'], request.user)
        messages.success(request, 'Activated XenForo account.')
        credentials = {
            'username': result['username'],
            'password': result['password'],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'XenForo'})

    else:
        logger.error("UnSuccessful attempt to activate xenforo for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your XenForo account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_xenforo_forum(request):
    logger.debug("deactivate_xenforo_forum called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = XenForoManager.disable_user(authinfo.xenforo_username)
    if result.status_code == 200:
        AuthServicesInfoManager.update_user_xenforo_info("", request.user)
        logger.info("Successfully deactivated XenForo for user %s" % request.user)
        messages.success(request, 'Deactivated XenForo account.')
    else:
        messages.error(request, 'An error occurred while processing your XenForo account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_xenforo_password(request):
    logger.debug("reset_xenforo_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = XenForoManager.reset_password(authinfo.xenforo_username)
    # Based on XenAPI's response codes
    if result['response']['status_code'] == 200:
        logger.info("Successfully reset XenForo password for user %s" % request.user)
        messages.success(request, 'Reset XenForo account password.')
        credentials = {
            'username': authinfo.xenforo_username,
            'password': result['password'],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'XenForo'})
    else:
        logger.error("Unsuccessful attempt to reset XenForo password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your XenForo account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def set_xenforo_password(request):
    logger.debug("set_xenforo_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = XenForoManager.update_user_password(authinfo.xenforo_username, password)
            if result['response']['status_code'] == 200:
                logger.info("Successfully reset XenForo password for user %s" % request.user)
                messages.success(request, 'Changed XenForo password.')
            else:
                logger.error("Failed to install custom XenForo password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your XenForo account.')
            return redirect('auth_services')
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Forum'}
    return render(request, 'registered/service_password.html', context=context)


@login_required
@members_and_blues()
def activate_ipboard_forum(request):
    logger.debug("activate_ipboard_forum called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding ipboard user for user %s with main character %s" % (request.user, character))
    result = IPBoardManager.add_user(character.character_name, request.user.email)
    if result[0] != "":
        AuthServicesInfoManager.update_user_ipboard_info(result[0], request.user)
        logger.debug("Updated authserviceinfo for user %s with ipboard credentials. Updating groups." % request.user)
        update_ipboard_groups.delay(request.user.pk)
        logger.info("Successfully activated ipboard for user %s" % request.user)
        messages.success(request, 'Activated IPBoard account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'IPBoard'})
    else:
        logger.error("UnSuccessful attempt to activate ipboard for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPBoard account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_ipboard_forum(request):
    logger.debug("deactivate_ipboard_forum called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = IPBoardManager.disable_user(authinfo.ipboard_username)
    # false we failed
    if result:
        AuthServicesInfoManager.update_user_ipboard_info("", request.user)
        logger.info("Successfully deactivated ipboard for user %s" % request.user)
        messages.success(request, 'Deactivated IPBoard account.')
    else:
        logger.error("Unsuccessful attempt to deactviate ipboard for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPBoard account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_ipboard_password(request):
    logger.debug("reset_ipboard_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = IPBoardManager.update_user_password(authinfo.ipboard_username, request.user.email)
    if result != "":
        logger.info("Successfully reset ipboard password for user %s" % request.user)
        messages.success(request, 'Reset IPBoard password.')
        credentials = {
            'username': authinfo.ipboard_username,
            'password': result,
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'IPBoard'})
    else:
        logger.error("UnSuccessful attempt to reset ipboard password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPBoard account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def activate_jabber(request):
    logger.debug("activate_jabber called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding jabber user for user %s with main character %s" % (request.user, character))
    info = OpenfireManager.add_user(character.character_name)
    # If our username is blank means we already had a user
    if info[0] is not "":
        AuthServicesInfoManager.update_user_jabber_info(info[0], request.user)
        logger.debug("Updated authserviceinfo for user %s with jabber credentials. Updating groups." % request.user)
        update_jabber_groups.delay(request.user.pk)
        logger.info("Successfully activated jabber for user %s" % request.user)
        messages.success(request, 'Activated jabber account.')
        credentials = {
            'username': info[0],
            'password': info[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Jabber'})
    else:
        logger.error("UnSuccessful attempt to activate jabber for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your jabber account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_jabber(request):
    logger.debug("deactivate_jabber called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = OpenfireManager.delete_user(authinfo.jabber_username)
    # If our username is blank means we failed
    if result:
        AuthServicesInfoManager.update_user_jabber_info("", request.user)
        logger.info("Successfully deactivated jabber for user %s" % request.user)
        messages.success(request, 'Deactivated jabber account.')
    else:
        logger.error("UnSuccessful attempt to deactivate jabber for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your jabber account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_jabber_password(request):
    logger.debug("reset_jabber_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = OpenfireManager.update_user_pass(authinfo.jabber_username)
    # If our username is blank means we failed
    if result != "":
        AuthServicesInfoManager.update_user_jabber_info(authinfo.jabber_username, request.user)
        logger.info("Successfully reset jabber password for user %s" % request.user)
        messages.success(request, 'Reset jabber password.')
        credentials = {
            'username': authinfo.jabber_username,
            'password': result,
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Jabber'})
    else:
        logger.error("Unsuccessful attempt to reset jabber for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your jabber account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def activate_mumble(request):
    logger.debug("activate_mumble called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    ticker = character.corporation_ticker

    if authinfo.state == BLUE_STATE:
        logger.debug("Adding mumble user for blue user %s with main character %s" % (request.user, character))
        # Blue members should have alliance ticker (if in alliance)
        if EveAllianceInfo.objects.filter(alliance_id=character.alliance_id).exists():
            alliance = EveAllianceInfo.objects.filter(alliance_id=character.alliance_id)[0]
            ticker = alliance.alliance_ticker
        result = MumbleManager.create_blue_user(ticker, character.character_name)
    else:
        logger.debug("Adding mumble user for user %s with main character %s" % (request.user, character))
        result = MumbleManager.create_user(ticker, character.character_name)
    # if its empty we failed
    if result[0] is not "":
        AuthServicesInfoManager.update_user_mumble_info(result[0], request.user)
        logger.debug("Updated authserviceinfo for user %s with mumble credentials. Updating groups." % request.user)
        update_mumble_groups.delay(request.user.pk)
        logger.info("Successfully activated mumble for user %s" % request.user)
        messages.success(request, 'Activated Mumble account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Mumble'})
    else:
        logger.error("Unsuccessful attempt to activate mumble for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Mumble account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_mumble(request):
    logger.debug("deactivate_mumble called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = MumbleManager.delete_user(authinfo.mumble_username)
    # if false we failed
    if result:
        AuthServicesInfoManager.update_user_mumble_info("", request.user)
        logger.info("Successfully deactivated mumble for user %s" % request.user)
        messages.success(request, 'Deactivated Mumble account.')
    else:
        logger.error("Unsuccessful attempt to deactivate mumble for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Mumble account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_mumble_password(request):
    logger.debug("reset_mumble_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = MumbleManager.update_user_password(authinfo.mumble_username)

    # if blank we failed
    if result != "":
        logger.info("Successfully reset mumble password for user %s" % request.user)
        messages.success(request, 'Reset Mumble password.')
        credentials = {
            'username': authinfo.mumble_username,
            'password': result,
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Mumble'})
    else:
        logger.error("UnSuccessful attempt to reset mumble password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Mumble account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def activate_teamspeak3(request):
    logger.debug("activate_teamspeak3 called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    ticker = character.corporation_ticker

    if authinfo.state == BLUE_STATE:
        logger.debug("Adding TS3 user for blue user %s with main character %s" % (request.user, character))
        # Blue members should have alliance ticker (if in alliance)
        if EveAllianceInfo.objects.filter(alliance_id=character.alliance_id).exists():
            alliance = EveAllianceInfo.objects.filter(alliance_id=character.alliance_id)[0]
            ticker = alliance.alliance_ticker
        result = Teamspeak3Manager.add_blue_user(character.character_name, ticker)
    else:
        logger.debug("Adding TS3 user for user %s with main character %s" % (request.user, character))
        result = Teamspeak3Manager.add_user(character.character_name, ticker)

    # if its empty we failed
    if result[0] is not "":
        AuthServicesInfoManager.update_user_teamspeak3_info(result[0], result[1], request.user)
        logger.debug("Updated authserviceinfo for user %s with TS3 credentials. Updating groups." % request.user)
        logger.info("Successfully activated TS3 for user %s" % request.user)
        messages.success(request, 'Activated TeamSpeak3 account.')
        return redirect("auth_verify_teamspeak3")
    logger.error("Unsuccessful attempt to activate TS3 for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your TeamSpeak3 account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def verify_teamspeak3(request):
    logger.debug("verify_teamspeak3 called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    if not authinfo.teamspeak3_uid:
        logger.warn("Unable to validate user %s teamspeak: no teamspeak data" % request.user)
        return redirect("auth_services")
    if request.method == "POST":
        form = TeamspeakJoinForm(request.POST)
        if form.is_valid():
            update_teamspeak3_groups.delay(request.user.pk)
            logger.debug("Validated user %s joined TS server" % request.user)
            return redirect("auth_services")
    else:
        form = TeamspeakJoinForm({'username': authinfo.teamspeak3_uid})
    context = {
        'form': form,
        'authinfo': authinfo,
    }
    return render(request, 'registered/teamspeakjoin.html', context=context)


@login_required
@members_and_blues()
def deactivate_teamspeak3(request):
    logger.debug("deactivate_teamspeak3 called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = Teamspeak3Manager.delete_user(authinfo.teamspeak3_uid)

    # if false we failed
    if result:
        AuthServicesInfoManager.update_user_teamspeak3_info("", "", request.user)
        logger.info("Successfully deactivated TS3 for user %s" % request.user)
        messages.success(request, 'Deactivated TeamSpeak3 account.')
    else:
        logger.error("Unsuccessful attempt to deactivate TS3 for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your TeamSpeak3 account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_teamspeak3_perm(request):
    logger.debug("reset_teamspeak3_perm called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Deleting TS3 user for user %s" % request.user)
    Teamspeak3Manager.delete_user(authinfo.teamspeak3_uid)

    if authinfo.state == BLUE_STATE:
        logger.debug(
            "Generating new permission key for blue user %s with main character %s" % (request.user, character))
        result = Teamspeak3Manager.generate_new_blue_permissionkey(authinfo.teamspeak3_uid, character.character_name,
                                                                   character.corporation_ticker)
    else:
        logger.debug("Generating new permission key for user %s with main character %s" % (request.user, character))
        result = Teamspeak3Manager.generate_new_permissionkey(authinfo.teamspeak3_uid, character.character_name,
                                                              character.corporation_ticker)

    # if blank we failed
    if result != "":
        AuthServicesInfoManager.update_user_teamspeak3_info(result[0], result[1], request.user)
        logger.debug("Updated authserviceinfo for user %s with TS3 credentials. Updating groups." % request.user)
        update_teamspeak3_groups.delay(request.user)
        logger.info("Successfully reset TS3 permission key for user %s" % request.user)
        messages.success(request, 'Reset TeamSpeak3 permission key.')
    else:
        logger.error("Unsuccessful attempt to reset TS3 permission key for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your TeamSpeak3 account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_discord(request):
    logger.debug("deactivate_discord called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = DiscordOAuthManager.delete_user(authinfo.discord_uid)
    if result:
        AuthServicesInfoManager.update_user_discord_info("", request.user)
        logger.info("Successfully deactivated discord for user %s" % request.user)
        messages.success(request, 'Deactivated Discord account.')
    else:
        logger.error("UnSuccessful attempt to deactivate discord for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Discord account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_discord(request):
    logger.debug("reset_discord called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = DiscordOAuthManager.delete_user(authinfo.discord_uid)
    if result:
        AuthServicesInfoManager.update_user_discord_info("", request.user)
        logger.info("Successfully deleted discord user for user %s - forwarding to discord activation." % request.user)
        return redirect("auth_activate_discord")
    logger.error("Unsuccessful attempt to reset discord for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your Discord account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def activate_discord(request):
    logger.debug("activate_discord called by user %s" % request.user)
    return redirect(DiscordOAuthManager.generate_oauth_redirect_url())


@login_required
@members_and_blues()
def discord_callback(request):
    logger.debug("Received Discord callback for activation of user %s" % request.user)
    code = request.GET.get('code', None)
    if not code:
        logger.warn("Did not receive OAuth code from callback of user %s" % request.user)
        return redirect("auth_services")
    user_id = DiscordOAuthManager.add_user(code)
    if user_id:
        AuthServicesInfoManager.update_user_discord_info(user_id, request.user)
        if settings.DISCORD_SYNC_NAMES:
            update_discord_nickname.delay(request.user.pk)
        update_discord_groups.delay(request.user.pk)
        logger.info("Successfully activated Discord for user %s" % request.user)
        messages.success(request, 'Activated Discord account.')
    else:
        logger.error("Failed to activate Discord for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Discord account.')
    return redirect("auth_services")


@login_required
@user_passes_test(superuser_test)
def discord_add_bot(request):
    return redirect(DiscordOAuthManager.generate_bot_add_url())


@login_required
@members_and_blues()
def set_forum_password(request):
    logger.debug("set_forum_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = Phpbb3Manager.update_user_password(authinfo.forum_username, authinfo.main_char_id,
                                                        password=password)
            if result != "":
                logger.info("Successfully set forum password for user %s" % request.user)
                messages.success('Set forum password.')
            else:
                logger.error("Failed to install custom forum password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your forum account.')
            return redirect("auth_services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Forum'}
    return render(request, 'registered/service_password.html', context=context)


@login_required
@members_and_blues()
def set_mumble_password(request):
    logger.debug("set_mumble_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = MumbleManager.update_user_password(authinfo.mumble_username, password=password)
            if result != "":
                logger.info("Successfully reset forum password for user %s" % request.user)
                messages.success(request, 'Set Mumble password.')
            else:
                logger.error("Failed to install custom mumble password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your Mumble account.')
            return redirect("auth_services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Mumble'}
    return render(request, 'registered/service_password.html', context=context)


@login_required
@members_and_blues()
def set_jabber_password(request):
    logger.debug("set_jabber_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = OpenfireManager.update_user_pass(authinfo.jabber_username, password=password)
            if result != "":
                logger.info("Successfully set jabber password for user %s" % request.user)
                messages.success(request, 'Set jabber password.')
            else:
                logger.error("Failed to install custom jabber password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your jabber account.')
            return redirect("auth_services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Jabber'}
    return render(request, 'registered/service_password.html', context=context)


@login_required
@members_and_blues()
def set_ipboard_password(request):
    logger.debug("set_ipboard_password called by user %s" % request.user)
    error = None
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = IPBoardManager.update_user_password(authinfo.ipboard_username, request.user.email,
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
@members_and_blues()
def activate_discourse(request):
    logger.debug("activate_discourse called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding discourse user for user %s with main character %s" % (request.user, character))
    result = DiscourseManager.add_user(character.character_name, request.user.email)
    if result[0] != "":
        AuthServicesInfoManager.update_user_discourse_info(result[0], request.user)
        logger.debug("Updated authserviceinfo for user %s with discourse credentials. Updating groups." % request.user)
        update_discourse_groups.delay(request.user.pk)
        logger.info("Successfully activated discourse for user %s" % request.user)
        messages.success('Activated Discourse account.')
        messages.warning('Do not lose your Discourse password. It cannot be reset through auth.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Discourse'})
    else:
        logger.error("Unsuccessful attempt to activate forum for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Discourse account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_discourse(request):
    logger.debug("deactivate_discourse called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = DiscourseManager.delete_user(authinfo.discourse_username)
    if result:
        AuthServicesInfoManager.update_user_discourse_info("", request.user)
        logger.info("Successfully deactivated discourse for user %s" % request.user)
        messages.success('Deactivated Discourse account.')
    else:
        logger.error("Unsuccessful attempt to activate discourse for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Discourse account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def activate_ips4(request):
    logger.debug("activate_ips4 called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding IPS4 user for user %s with main character %s" % (request.user, character))
    result = Ips4Manager.add_user(character.character_name, request.user.email)
    # if empty we failed
    if result[0] != "":
        AuthServicesInfoManager.update_user_ips4_info(result[0], result[2], request.user)
        logger.debug("Updated authserviceinfo for user %s with IPS4 credentials." % request.user)
        # update_ips4_groups.delay(request.user.pk)
        logger.info("Successfully activated IPS4 for user %s" % request.user)
        messages.success(request, 'Activated IPSuite4 account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'IPSuite4'})
    else:
        logger.error("UnSuccessful attempt to activate IPS4 for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPSuite4 account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_ips4_password(request):
    logger.debug("reset_ips4_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = Ips4Manager.update_user_password(authinfo.ips4_username)
    # false we failed
    if result != "":
        logger.info("Successfully reset IPS4 password for user %s" % request.user)
        messages.success(request, 'Reset IPSuite4 password.')
        credentials = {
            'username': authinfo.ips4_username,
            'password': result,
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'IPSuite4'})
    else:
        logger.error("Unsuccessful attempt to reset IPS4 password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPSuite4 account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def set_ips4_password(request):
    logger.debug("set_ips4_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = Ips4Manager.update_custom_password(authinfo.ips4_username, plain_password=password)
            if result != "":
                logger.info("Successfully set IPS4 password for user %s" % request.user)
                messages.success(request, 'Set IPSuite4 password.')
            else:
                logger.error("Failed to install custom IPS4 password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your IPSuite4 account.')
            return redirect('auth_services')
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'IPS4'}
    return render(request, 'registered/service_password.html', context=context)


@login_required
@members_and_blues()
def deactivate_ips4(request):
    logger.debug("deactivate_ips4 called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = Ips4Manager.delete_user(authinfo.ips4_id)
    if result != "":
        AuthServicesInfoManager.update_user_ips4_info("", "", request.user)
        logger.info("Successfully deactivated IPS4 for user %s" % request.user)
        messages.success(request, 'Deactivated IPSuite4 account.')
    else:
        logger.error("UnSuccessful attempt to deactivate IPS4 for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your IPSuite4 account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def activate_smf(request):
    logger.debug("activate_smf called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding smf user for user %s with main character %s" % (request.user, character))
    result = smfManager.add_user(character.character_name, request.user.email, ['Member'], authinfo.main_char_id)
    # if empty we failed
    if result[0] != "":
        AuthServicesInfoManager.update_user_smf_info(result[0], request.user)
        logger.debug("Updated authserviceinfo for user %s with smf credentials. Updating groups." % request.user)
        update_smf_groups.delay(request.user.pk)
        logger.info("Successfully activated smf for user %s" % request.user)
        messages.success(request, 'Activated SMF account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'SMF'})
    else:
        logger.error("UnSuccessful attempt to activate smf for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your SMF account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_smf(request):
    logger.debug("deactivate_smf called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = smfManager.disable_user(authinfo.smf_username)
    # false we failed
    if result:
        AuthServicesInfoManager.update_user_smf_info("", request.user)
        logger.info("Successfully deactivated smf for user %s" % request.user)
        messages.success(request, 'Deactivated SMF account.')
    else:
        logger.error("UnSuccessful attempt to activate smf for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your SMF account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_smf_password(request):
    logger.debug("reset_smf_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = smfManager.update_user_password(authinfo.smf_username, authinfo.main_char_id)
    # false we failed
    if result != "":
        logger.info("Successfully reset smf password for user %s" % request.user)
        messages.success(request, 'Reset SMF password.')
        credentials = {
            'username': authinfo.smf_username,
            'password': result,
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'SMF'})
    else:
        logger.error("Unsuccessful attempt to reset smf password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your SMF account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def set_smf_password(request):
    logger.debug("set_smf_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = smfManager.update_user_password(authinfo.smf_username, authinfo.main_char_id, password=password)
            if result != "":
                logger.info("Successfully set smf password for user %s" % request.user)
                messages.success(request, 'Set SMF password.')
            else:
                logger.error("Failed to install custom smf password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your SMF account.')
            return redirect("auth_services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'SMF'}
    return render(request, 'registered/service_password.html', context=context)


@login_required
@members_and_blues()
def activate_market(request):
    logger.debug("activate_market called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    logger.debug("Adding market user for user %s with main character %s" % (request.user, character))
    result = marketManager.add_user(character.character_name, request.user.email, authinfo.main_char_id,
                                    character.character_name)
    # if empty we failed
    if result[0] != "":
        AuthServicesInfoManager.update_user_market_info(result[0], request.user)
        logger.debug("Updated authserviceinfo for user %s with market credentials." % request.user)
        logger.info("Successfully activated market for user %s" % request.user)
        messages.success(request, 'Activated Alliance Market account.')
        credentials = {
            'username': result[0],
            'password': result[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Alliance Market'})
    else:
        logger.error("UnSuccessful attempt to activate market for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Alliance Market account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_market(request):
    logger.debug("deactivate_market called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = marketManager.disable_user(authinfo.market_username)
    # false we failed
    if result:
        AuthServicesInfoManager.update_user_market_info("", request.user)
        logger.info("Successfully deactivated market for user %s" % request.user)
        messages.success(request, 'Deactivated Alliance Market account.')
    else:
        logger.error("UnSuccessful attempt to activate market for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Alliance Market account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_market_password(request):
    logger.debug("reset_market_password called by user %s" % request.user)
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    result = marketManager.update_user_password(authinfo.market_username)
    # false we failed
    if result != "":
        logger.info("Successfully reset market password for user %s" % request.user)
        messages.success(request, 'Reset Alliance Market password.')
        credentials = {
            'username': authinfo.market_username,
            'password': result,
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Alliance Market'})
    else:
        logger.error("Unsuccessful attempt to reset market password for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your Alliance Market account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def set_market_password(request):
    logger.debug("set_market_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            result = marketManager.update_custom_password(authinfo.market_username, password)
            if result != "":
                logger.info("Successfully reset market password for user %s" % request.user)
                messages.success(request, 'Set Alliance Market password.')
            else:
                logger.error("Failed to install custom market password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your Alliance Market account.')
            return redirect("auth_services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Market'}
    return render(request, 'registered/service_password.html', context=context)
