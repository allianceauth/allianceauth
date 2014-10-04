from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from evespecific.managers import EveCharacterManager

# Create your views here.
@login_required
def index(request):
    return render_to_response('public/index.html',None, context_instance=RequestContext(request))

@login_required
def characters_view(request):
    characterManager = EveCharacterManager()
    
    render_items = {'characters':characterManager.get_characters_by_owner_id(request.user.id)}
    return render_to_response('public/characters.html', render_items, context_instance=RequestContext(request))

@login_required
def apikeymanagment_view(request):
    render_items = {}
    return render_to_response('public/apikeymanagment.html', render_items, context_instance=RequestContext(request))
