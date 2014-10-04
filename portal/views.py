from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from forms import UpdateKeyForm
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
    if request.method == 'POST':
        form = UpdateKeyForm(request.POST)

        if form.is_valid():

            return HttpResponseRedirect("/")
    else:
        form = UpdateKeyForm(initial={'api_id':request.user.api_id,'api_key':request.user.api_key})

    return render_to_response('public/apikeymanagment.html', {'form':form}, context_instance=RequestContext(request))
