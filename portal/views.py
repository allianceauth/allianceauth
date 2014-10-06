from django.shortcuts import render_to_response, HttpResponseRedirect

from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from evespecific.managers import EveCharacterManager
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
    characterManager = EveCharacterManager()
    
    render_items = {'characters':characterManager.get_characters_by_owner_id(request.user.id)}
    return render_to_response('registered/characters.html', render_items, context_instance=RequestContext(request))


@login_required
def api_key_management_view(request):
    if request.method == 'POST':
        form = UpdateKeyForm(request.POST)

        if form.is_valid():

            return HttpResponseRedirect("/")
    else:
        form = UpdateKeyForm(initial={'api_id':request.user.api_id,'api_key':request.user.api_key})

    return render_to_response('registered/apikeymanagment.html', {'form':form}, context_instance=RequestContext(request))


@login_required
def applications_view(request):
    return render_to_response('registered/applications.html', None, context_instance=RequestContext(request))


@login_required
def main_character_change(request, id):
    userManager = AllianceUserManager()
    characterManager = EveCharacterManager()
    if characterManager.check_if_character_owned_by_user(id,request.user.id) == True:
        userManager.update_user_main_character(id,request.user.id)
        return HttpResponseRedirect("/")
    return HttpResponseRedirect("/characters")


@login_required
def activate_forum(request):
    userManager = AllianceUserManager()
    forumManager = Phpbb3Manager()

    if userManager.check_if_user_exist(request.user.id):
        # Valid now we get the main characters
        characterManager = EveCharacterManager()
        character = characterManager.get_character_by_id(request.user.main_char_id)
        
        if forumManager.check_user(character.character_name) == False:
            forumManager.add_user(character.character_name, "test", request.user.email, ['REGISTERED'])
            return HttpResponseRedirect("/applications/")

    return HttpResponseRedirect("/")


@login_required
def activate_jabber(request):
    userManager = AllianceUserManager()
    jabberManager = JabberManager()
    if userManager.check_if_user_exist(request.user.id):
        characterManager = EveCharacterManager()
        character = characterManager.get_character_by_id(request.user.main_char_id)
    
        jabberManager.add_user(character.character_name,"test")
    
        return HttpResponseRedirect("/applications/")
    
    return HttpResponseRedirect("/")


@login_required
def activate_mumble(request):
    userManager = AllianceUserManager()
    characterManager = EveCharacterManager()
    mumbleManager = MumbleManager()

    if userManager.check_if_user_exist(request.user.id):
        characterManager = EveCharacterManager()
        character = characterManager.get_character_by_id(request.user.main_char_id)

        mumbleManager.create_user(character.character_name, "test")

        return HttpResponseRedirect("/applications/")

    return HttpResponseRedirect("/")