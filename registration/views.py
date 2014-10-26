from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import RegistrationForm


def register_user_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():

            if not User.objects.filter(username=form.cleaned_data['username']).exists():
                user = User.objects.create_user(form.cleaned_data['username'],
                                                form.cleaned_data['email'], form.cleaned_data['password'])

                user.save()

                return HttpResponseRedirect("/dashboard")

            else:
                return render_to_response('public/register.html', {'form': form, 'error': True}
                                          , context_instance=RequestContext(request))

    else:
        form = RegistrationForm()

    return render_to_response('public/register.html', {'form': form}, context_instance=RequestContext(request))