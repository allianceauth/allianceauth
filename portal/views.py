from django.shortcuts import render_to_response, HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission

from services.eveapi_manager import EveApiManager
from evespecific.managers import EveManager
from authentication.models import AllianceUserManager
from services.phpbb3_manager import Phpbb3Manager
from services.jabber_manager import JabberManager
from services.mumble_manager import MumbleManager

from forms import UpdateKeyForm


def index_view(request):
    return render_to_response('public/index.html', None, context_instance=RequestContext(request))


@login_required
def dashboard_view(request):
    return render_to_response('registered/dashboard.html', None, context_instance=RequestContext(request))


@login_required
def characters_view(request):
    evemanager = EveManager()
    
    render_items = {'characters': evemanager.get_characters_by_owner_id(request.user.id)}
    return render_to_response('registered/characters.html', render_items, context_instance=RequestContext(request))


@login_required
def api_key_management_view(request):
    api = EveApiManager()
    evemanager = EveManager()

    if request.method == 'POST':
        form = UpdateKeyForm(request.POST)

        if form.is_valid():
            evemanager.create_api_keypair(form.cleaned_data['api_id'],
                                          form.cleaned_data['api_key'],
                                          request.user)

            # Grab characters associated with the key pair

            characters = api.get_characters_from_api(form.cleaned_data['api_id'], form.cleaned_data['api_key'])
            evemanager.create_characters_from_list(characters, request.user, form.cleaned_data['api_id'])
            return HttpResponseRedirect("/api_key_management/")
    else:
        form = UpdateKeyForm()
    context = {'form': form, 'apikeypairs': evemanager.get_api_key_pairs(request.user.id)}
    return render_to_response('registered/apikeymanagment.html', context,
                              context_instance=RequestContext(request))


@login_required
def api_key_removal(request, api_id):
    evemanager = EveManager()
    usermanager = AllianceUserManager()
    # Check if our users main id is in the to be deleted characters
    characters = evemanager.get_characters_by_owner_id(request.user.id)
    if characters is not None:
        for character in characters:
            if character.character_id == request.user.main_char_id:
                # TODO: Remove servies also
                usermanager.update_user_main_character("", request.user.id)

    evemanager.delete_api_key_pair(api_id, request.user.id)
    evemanager.delete_characters_by_api_id(api_id, request.user.id)

    return HttpResponseRedirect("/api_key_management/")


@login_required
def applications_view(request):
    return render_to_response('registered/applications.html', None, context_instance=RequestContext(request))


@login_required
def main_character_change(request, char_id):
    usermanager = AllianceUserManager()
    charactermanager = EveManager()
    if charactermanager.check_if_character_owned_by_user(char_id, request.user):
        usermanager.update_user_main_character(char_id, request.user.id)
        # Check if character is in the alliance
        if charactermanager.get_charater_alliance_id_by_id(char_id) == settings.ALLIANCE_ID:
            usermanager.add_alliance_member_permission(request.user.id)
        else:
            #TODO: disable serivces
            usermanager.remove_alliance_member_permission(request.user.id)

        return HttpResponseRedirect("/characters")
    return HttpResponseRedirect("/characters")


@login_required
@permission_required('auth.alliance_member')
def activate_forum(request):
    userManager = AllianceUserManager()
    forumManager = Phpbb3Manager()

    if userManager.check_if_user_exist(request.user.id):
        # Valid now we get the main characters
        characterManager = EveManager()
        character = characterManager.get_character_by_id(request.user.main_char_id)
        
        if forumManager.check_user(character.character_name) == False:
            forumManager.add_user(character.character_name, "test", request.user.email, ['REGISTERED'])
            return HttpResponseRedirect("/applications/")

    return HttpResponseRedirect("/")


@login_required
@permission_required('auth.alliance_member')
def activate_jabber(request):
    userManager = AllianceUserManager()
    jabberManager = JabberManager()
    if userManager.check_if_user_exist(request.user.id):
        characterManager = EveManager()
        character = characterManager.get_character_by_id(request.user.main_char_id)
    
        jabberManager.add_user(character.character_name,"test")
    
        return HttpResponseRedirect("/applications/")
    
    return HttpResponseRedirect("/")


@login_required
@permission_required('auth.alliance_member')
def activate_mumble(request):
    userManager = AllianceUserManager()
    characterManager = EveManager()
    mumbleManager = MumbleManager()

    if userManager.check_if_user_exist(request.user.id):
        characterManager = EveManager()
        character = characterManager.get_character_by_id(request.user.main_char_id)

        mumbleManager.create_user(character.character_name, "test")

        return HttpResponseRedirect("/applications/")

    return HttpResponseRedirect("/")