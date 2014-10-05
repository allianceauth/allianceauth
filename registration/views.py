from django.http import Http404,HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from authentication.models import AllianceUserManager
from evespecific.managers import EveApiManager

from forms import RegistrationForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            userManager = AllianceUserManager()
            user = userManager.create_user_withapi(
                form.cleaned_data['username'],
                form.cleaned_data['email'],
                form.cleaned_data['password'],
                form.cleaned_data['api_id'],
                form.cleaned_data['api_key']
            )
            
            # Populate character data
            api = EveApiManager()
            api.CreateCharactersFromID(form.cleaned_data['api_id'], form.cleaned_data['api_key'], user)

            return HttpResponseRedirect("/")
    else:
        form = RegistrationForm()

    return render_to_response('public/register.html', {'form': form}, context_instance=RequestContext(request))
