from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from managers.jabber_manager import JabberManager
from managers.forum_manager import ForumManager
from managers.mumble_manager import MumbleManager

from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager

from celerytask.tasks import update_jabber_groups
from celerytask.tasks import update_mumble_groups
from celerytask.tasks import update_forum_groups


@login_required
def services_view(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)

    return render_to_response('registered/services.html', {'authinfo': authinfo}, context_instance=RequestContext(request))

@login_required
@permission_required('auth.alliance_member')
def activate_forum(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    # Valid now we get the main characters
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    result = ForumManager.add_user(character.character_name, request.user.email, ['REGISTERED'])
    # if empty we failed
    if result[0] != "":
        AuthServicesInfoManager.update_user_forum_info(result[0], result[1], request.user)
        update_forum_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@permission_required('auth.alliance_member')
def deactivate_forum(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = ForumManager.disable_user(authinfo.forum_username)
    # false we failed
    if result:
        AuthServicesInfoManager.update_user_forum_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@permission_required('auth.alliance_member')
def reset_forum_password(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = ForumManager.update_user_password(authinfo.forum_username)
    # false we failed
    if result != "":
        AuthServicesInfoManager.update_user_forum_info(authinfo.forum_username, result, request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@permission_required('auth.alliance_member')
def activate_jabber(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    info = JabberManager.add_user(character.character_name)
    # If our username is blank means we already had a user
    if info[0] is not "":
        AuthServicesInfoManager.update_user_jabber_info(info[0], info[1], request.user)
        update_jabber_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@permission_required('auth.alliance_member')
def deactivate_jabber(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = JabberManager.delete_user(authinfo.jabber_username)
    # If our username is blank means we failed
    if result:
        AuthServicesInfoManager.update_user_jabber_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@permission_required('auth.alliance_member')
def reset_jabber_password(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = JabberManager.update_user_pass(authinfo.jabber_username)
    # If our username is blank means we failed
    if result != "":
        AuthServicesInfoManager.update_user_jabber_info(authinfo.jabber_username, result, request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@permission_required('auth.alliance_member')
def activate_mumble(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    character = EveManager.get_character_by_id(authinfo.main_char_id)
    result = MumbleManager.create_user(character.corporation_ticker, character.character_name)
    # if its empty we failed
    if result[0] is not "":
        AuthServicesInfoManager.update_user_mumble_info(result[0], result[1], request.user)
        update_mumble_groups(request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/dashboard")


@login_required
@permission_required('auth.alliance_member')
def deactivate_mumble(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = MumbleManager.delete_user(authinfo.mumble_username)
    # if false we failed
    if result:
        AuthServicesInfoManager.update_user_mumble_info("", "", request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/")


@login_required
@permission_required('auth.alliance_member')
def reset_mumble_password(request):
    authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
    result = MumbleManager.update_user_password(authinfo.mumble_username)
    # if blank we failed
    if result != "":
        AuthServicesInfoManager.update_user_mumble_info(authinfo.mumble_username, result, request.user)
        return HttpResponseRedirect("/services/")
    return HttpResponseRedirect("/")