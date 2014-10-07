from django.http import Http404,HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from authentication.models import AllianceUserManager
from evespecific.managers import EveManager
from services.eveapi_manager import EveApiManager

from forms import RegistrationForm


def register(request):
    api = EveApiManager()
    evemanager = EveManager()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            usermanager = AllianceUserManager()
            if not usermanager.check_if_user_exist_by_name(form.cleaned_data['username']):
                user = usermanager.create_user(
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password']
                )

                return HttpResponseRedirect("/dashboard")

            else:
                return render_to_response('public/register.html', {'form': form, 'error': True}
                                          , context_instance=RequestContext(request))

    else:
        form = RegistrationForm()

    return render_to_response('public/register.html', {'form': form}, context_instance=RequestContext(request))
