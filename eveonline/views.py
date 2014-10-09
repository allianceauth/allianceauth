from util import add_member_permission
from util import remove_member_permission
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from forms import UpdateKeyForm
from managers import EveManager

from authentication.managers import AuthServicesInfoManager
from services.managers.eve_api_manager import EveApiManager


@login_required
def api_key_management_view(request):

    if request.method == 'POST':
        form = UpdateKeyForm(request.POST)

        if form.is_valid():
            EveManager.create_api_keypair(form.cleaned_data['api_id'],
                                          form.cleaned_data['api_key'],
                                          request.user)

            # Grab characters associated with the key pair

            characters = EveApiManager.get_characters_from_api(form.cleaned_data['api_id'], form.cleaned_data['api_key'])
            EveManager.create_characters_from_list(characters, request.user, form.cleaned_data['api_id'])
            return HttpResponseRedirect("/api_key_management/")
    else:
        form = UpdateKeyForm()
    context = {'form': form, 'apikeypairs': EveManager.get_api_key_pairs(request.user.id)}
    return render_to_response('registered/apikeymanagment.html', context,
                              context_instance=RequestContext(request))


@login_required
def api_key_removal(request, api_id):
    # Check if our users main id is in the to be deleted characters
    characters = EveManager.get_characters_by_owner_id(request.user.id)
    if characters is not None:
        for character in characters:
            if character.character_id == request.user.main_char_id:
                # TODO: Remove servies also
                AuthServicesInfoManager.update_main_char_Id("", request.user.id)

    EveManager.delete_api_key_pair(api_id, request.user.id)
    EveManager.delete_characters_by_api_id(api_id, request.user.id)

    return HttpResponseRedirect("/api_key_management/")


@login_required
def characters_view(request):

    render_items = {'characters': EveManager.get_characters_by_owner_id(request.user.id),
                    'authinfo': AuthServicesInfoManager.get_auth_service_info(request.user)}
    return render_to_response('registered/characters.html', render_items, context_instance=RequestContext(request))


@login_required
def main_character_change(request, char_id):

    if EveManager.check_if_character_owned_by_user(char_id, request.user):
        AuthServicesInfoManager.update_main_char_Id(char_id, request.user)
        # Check if character is in the alliance
        if EveManager.get_charater_alliance_id_by_id(char_id) == settings.ALLIANCE_ID:
            add_member_permission(request.user, 'alliance_member')
        else:
            #TODO: disable serivces
            remove_member_permission(request.user, 'alliance_member')

        return HttpResponseRedirect("/characters")
    return HttpResponseRedirect("/characters")