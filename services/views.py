from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test

from eveonline.models import EveCharacter
from authentication.models import AuthServicesInfo
from managers.openfire_manager import OpenfireManager
from managers.phpbb3_manager import Phpbb3Manager
from managers.mumble_manager import MumbleManager
from managers.ipboard_manager import IPBoardManager
from managers.teamspeak3_manager import Teamspeak3Manager
from managers.discord_manager import DiscordManager
from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager
from celerytask.tasks import remove_all_syncgroups_for_service
from celerytask.tasks import update_jabber_groups
from celerytask.tasks import update_mumble_groups
from celerytask.tasks import update_forum_groups
from celerytask.tasks import update_ipboard_groups
from celerytask.tasks import update_teamspeak3_groups
from celerytask.tasks import update_discord_groups
from forms import JabberBroadcastForm
from forms import FleetFormatterForm
from util import check_if_user_has_permission

import threading
import datetime 


@login_required
def fleet_formatter_view(request):
    if request.method == 'POST':
        form = FleetFormatterForm(request.POST)
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
    else:
        form = FleetFormatterForm()
        generated = ""

    context = {'form': form, 'generated': generated}

    return render_to_response('registered/fleetformattertool.html', context, context_instance=RequestContext(request))

@login_required
@permission_required('auth.jabber_broadcast')
def jabber_broadcast_view(request):
    success = False
    if request.method == 'POST':
        form = JabberBroadcastForm(request.POST)
        if form.is_valid():
            user_info = AuthServicesInfo.objects.get(user=request.user)
            main_char = EveCharacter.objects.get(character_id=user_info.main_char_id)
            if user_info.main_char_id != "":
                message_to_send = form.cleaned_data['message'] + "\n##### SENT BY: " + "[" + main_char.corporation_ticker + "]" + main_char.character_name + " TO: " + form.cleaned_data['group'] + " WHEN: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + " #####\n##### Replies are NOT monitored #####\n"
                group_to_send = form.cleaned_data['group']

                OpenfireManager.send_broadcast_threaded(group_to_send, message_to_send,)

            else:
                message_to_send = form.cleaned_data['message'] + "\n##### SENT BY: " + "No character but can send pings?" + " TO: " + form.cleaned_data['group'] + " WHEN: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + " #####\n##### Replies are NOT monitored #####\n"
                group_to_send = form.cleaned_data['group']

                OpenfireManager.send_broadcast_threaded(group_to_send, message_to_send,)

            success = True
    else:
        form = JabberBroadcastForm()

    context = {'form': form, 'success': success}
    return render_to_response('registered/jabberbroadcast.html', context, context_instance=RequestContext(request))


@login_required
def services_view(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)

    return render_to_response('registered/services.html', {'authinfo': authinfo},
                              context_instance=RequestContext(request))


def service_blue_alliance_test(user):
    return check_if_user_has_permission(user, 'member') or check_if_user_has_permission(user, 'blue_member')


@login_required
@user_passes_test(service_blue_alliance_test)
def activate_forum(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    result = Phpbb3Manager.add_user(character.character_name, request.user.email, ['REGISTERED'], authinfo.main_char_id)
    # if empty we failed
    if result[0] != "":
        AuthServicesInfoManager.update_user_forum_info(result[0], result[1], request.user)
        update_forum_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def deactivate_forum(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = Phpbb3Manager.disable_user(authinfo.forum_username)
    remove_all_syncgroups_for_service(request.user, "phpbb")
    # false we failed
    if result:
        AuthServicesInfoManager.update_user_forum_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def reset_forum_password(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = Phpbb3Manager.update_user_password(authinfo.forum_username, authinfo.main_char_id)
    # false we failed
    if result != "":
        AuthServicesInfoManager.update_user_forum_info(authinfo.forum_username, result, request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def activate_ipboard_forum(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    result = IPBoardManager.add_user(character.character_name, request.user.email)
    if result[0] != "":
        AuthServicesInfoManager.update_user_ipboard_info(result[0], result[1], request.user)
        update_ipboard_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def deactivate_ipboard_forum(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = IPBoardManager.disable_user(authinfo.ipboard_username)
    remove_all_syncgroups_for_service(request.user, "ipboard")
    # false we failed
    if result:
        AuthServicesInfoManager.update_user_ipboard_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def reset_ipboard_password(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = IPBoardManager.update_user_password(authinfo.ipboard_username, request.user.email)
    if result != "":
        AuthServicesInfoManager.update_user_ipboard_info(authinfo.ipboard_username, result, request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def activate_jabber(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    info = OpenfireManager.add_user(character.character_name)
    # If our username is blank means we already had a user
    if info[0] is not "":
        AuthServicesInfoManager.update_user_jabber_info(info[0], info[1], request.user)
        update_jabber_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def deactivate_jabber(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = OpenfireManager.delete_user(authinfo.jabber_username)
    remove_all_syncgroups_for_service(request.user, "openfire")
    # If our username is blank means we failed
    if result:
        AuthServicesInfoManager.update_user_jabber_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def reset_jabber_password(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = OpenfireManager.update_user_pass(authinfo.jabber_username)
    # If our username is blank means we failed
    if result != "":
        AuthServicesInfoManager.update_user_jabber_info(authinfo.jabber_username, result, request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def activate_mumble(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    if check_if_user_has_permission(request.user, "blue_member"):
        result = MumbleManager.create_blue_user(character.corporation_ticker, character.character_name)
    else:
        result = MumbleManager.create_user(character.corporation_ticker, character.character_name)
    # if its empty we failed
    if result[0] is not "":
        AuthServicesInfoManager.update_user_mumble_info(result[0], result[1], request.user)
        update_mumble_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def deactivate_mumble(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = MumbleManager.delete_user(authinfo.mumble_username)
    remove_all_syncgroups_for_service(request.user, "mumble")
    # if false we failed
    if result:
        AuthServicesInfoManager.update_user_mumble_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/")


@login_required
@user_passes_test(service_blue_alliance_test)
def reset_mumble_password(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = MumbleManager.update_user_password(authinfo.mumble_username)

    # if blank we failed
    if result != "":
        AuthServicesInfoManager.update_user_mumble_info(authinfo.mumble_username, result, request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/")


@login_required
@user_passes_test(service_blue_alliance_test)
def activate_teamspeak3(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    if check_if_user_has_permission(request.user, "blue_member"):
        result = Teamspeak3Manager.add_blue_user(character.character_name, character.corporation_ticker)
    else:
        result = Teamspeak3Manager.add_user(character.character_name, character.corporation_ticker)

    # if its empty we failed
    if result[0] is not "":
        AuthServicesInfoManager.update_user_teamspeak3_info(result[0], result[1], request.user)
        update_teamspeak3_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@user_passes_test(service_blue_alliance_test)
def deactivate_teamspeak3(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = Teamspeak3Manager.delete_user(authinfo.teamspeak3_uid)

    remove_all_syncgroups_for_service(request.user, "teamspeak3")

    # if false we failed
    if result:
        AuthServicesInfoManager.update_user_teamspeak3_info("", "", request.user)

        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/")


@login_required
@user_passes_test(service_blue_alliance_test)
def reset_teamspeak3_perm(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    character = EveManager.get_character_by_id(authinfo.main_char_id)

    Teamspeak3Manager.delete_user(authinfo.teamspeak3_uid)

    remove_all_syncgroups_for_service(request.user, "teamspeak3")

    if check_if_user_has_permission(request.user, "blue_member"):
        result = Teamspeak3Manager.generate_new_blue_permissionkey(authinfo.teamspeak3_uid, character.character_name,
                                                                   character.corporation_ticker)
    else:
        result = Teamspeak3Manager.generate_new_permissionkey(authinfo.teamspeak3_uid, character.character_name,
                                                              character.corporation_ticker)

    # if blank we failed
    if result != "":
        AuthServicesInfoManager.update_user_teamspeak3_info(result[0], result[1], request.user)
        update_teamspeak3_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/")

@login_required
def fleet_fits(request):
    context = {}
    return render_to_response('registered/fleetfits.html', context,
context_instance=RequestContext(request))

@login_required
@user_passes_test(service_blue_alliance_test)
def activate_discord(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    info = DiscordManager.add_user(character.character_name)
    # If our username is blank means we already had a user
    if info[0] is not "":
        AuthServicesInfoManager.update_user_discord_info(info[0], info[1], request.user)
        update_discord_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")

@login_required
@user_passes_test(service_blue_alliance_test)
def deactivate_discord(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = DiscordManager.delete_user(authinfo.discord_username)
    remove_all_syncgroups_for_service(request.user, "discord")
    if result:
        AuthServicesInfoManager.update_user_discord_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")

@login_required
@user_passes_test(service_blue_alliance_test)
def reset_discord(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = DiscordManager.delete_user(authinfo.discord_username)
    if result:
        # ensures succesful deletion
        AuthServicesInfoManager.update_user_discord_info("", "", request.user)
        new_result = DiscordManager.add_user(authinfo.discord_username)
        if new_result:
            # ensures succesful creation
            AuthServicesInfoManager.update_user_discord_info(new_result[0], new_result[1], request.user)
            update_discord_groups(request.user)
            return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/services/")
