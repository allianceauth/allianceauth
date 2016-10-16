from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from eveonline.forms import UpdateKeyForm
from eveonline.managers import EveManager
from authentication.managers import AuthServicesInfoManager
from services.managers.eve_api_manager import EveApiManager
from eveonline.models import EveApiKeyPair
from authentication.models import AuthServicesInfo
from authentication.tasks import set_state
from eveonline.tasks import refresh_api

import logging

logger = logging.getLogger(__name__)


@login_required
def add_api_key(request):
    logger.debug("add_api_key called by user %s" % request.user)
    if request.method == 'POST':
        form = UpdateKeyForm(request.user, request.POST)
        logger.debug("Request type POST with form valid: %s" % form.is_valid())
        if form.is_valid():
            EveManager.create_api_keypair(form.cleaned_data['api_id'],
                                          form.cleaned_data['api_key'],
                                          request.user)

            # Grab characters associated with the key pair
            characters = EveApiManager.get_characters_from_api(form.cleaned_data['api_id'],
                                                               form.cleaned_data['api_key'])
            EveManager.create_characters_from_list(characters, request.user, form.cleaned_data['api_id'])
            logger.info("Successfully processed api add form for user %s" % request.user)
            messages.success(request, 'Added API key %s to your account.' % form.cleaned_data['api_id'])
            auth = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
            if not auth.main_char_id:
                messages.warning(request, 'Please select a main character.')
            return redirect("/api_key_management/")
        else:
            logger.debug("Form invalid: returning to form.")
    else:
        logger.debug("Providing empty update key form for user %s" % request.user)
        form = UpdateKeyForm(request.user)
    context = {'form': form, 'apikeypairs': EveManager.get_api_key_pairs(request.user.id)}
    return render(request, 'registered/addapikey.html', context=context)


@login_required
def api_key_management_view(request):
    logger.debug("api_key_management_view called by user %s" % request.user)
    context = {'apikeypairs': EveManager.get_api_key_pairs(request.user.id)}

    return render(request, 'registered/apikeymanagment.html', context=context)


@login_required
def api_key_removal(request, api_id):
    logger.debug("api_key_removal called by user %s for api id %s" % (request.user, api_id))
    authinfo = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
    # Check if our users main id is in the to be deleted characters
    characters = EveManager.get_characters_by_owner_id(request.user.id)
    if characters is not None:
        for character in characters:
            if character.character_id == authinfo.main_char_id:
                if character.api_id == api_id:
                    messages.warning(request,
                                     'You have deleted your main character. Please select a new main character.')
                    set_state(request.user)

    EveManager.delete_api_key_pair(api_id, request.user.id)
    EveManager.delete_characters_by_api_id(api_id, request.user.id)
    messages.success(request, 'Deleted API key %s' % api_id)
    logger.info("Succesfully processed api delete request by user %s for api %s" % (request.user, api_id))
    return redirect("auth_api_key_management")


@login_required
def characters_view(request):
    logger.debug("characters_view called by user %s" % request.user)
    render_items = {'characters': EveManager.get_characters_by_owner_id(request.user.id),
                    'authinfo': AuthServicesInfo.objects.get_or_create(user=request.user)[0]}
    return render(request, 'registered/characters.html', context=render_items)


@login_required
def main_character_change(request, char_id):
    logger.debug("main_character_change called by user %s for character id %s" % (request.user, char_id))
    if EveManager.check_if_character_owned_by_user(char_id, request.user):
        AuthServicesInfoManager.update_main_char_id(char_id, request.user)
        set_state(request.user)
        messages.success(request, 'Changed main character ID to %s' % char_id)
        return redirect("auth_characters")
    messages.error(request, 'Failed to change main character - selected character is not owned by your account.')
    return redirect("auth_characters")


@login_required
def user_refresh_api(request, api_id):
    logger.debug("user_refresh_api called by user %s for api id %s" % (request.user, api_id))
    if EveApiKeyPair.objects.filter(api_id=api_id).exists():
        api_key_pair = EveApiKeyPair.objects.get(api_id=api_id)
        if api_key_pair.user == request.user:
            refresh_api(api_key_pair)
            messages.success(request, 'Refreshed API key %s' % api_id)
            set_state(request.user)
        else:
            messages.warning(request, 'You are not authorized to refresh that API key.')
            logger.warn("User %s not authorized to refresh api id %s" % (request.user, api_id))
    else:
        messages.warning(request, 'Unable to locate API key %s' % api_id)
        logger.warn("User %s unable to refresh api id %s - api key not found" % (request.user, api_id))
    return redirect("auth_api_key_management")
