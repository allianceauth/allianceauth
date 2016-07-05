from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation

from forms import RegistrationForm

import logging

logger = logging.getLogger(__name__)

def register_user_view(request):
    logger.debug("register_user_view called by user %s" % request.user)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():

            if not User.objects.filter(username=form.cleaned_data['username']).exists():
                user = User.objects.create_user(form.cleaned_data['username'],
                                                form.cleaned_data['email'], form.cleaned_data['password'])

                user.save()
                logger.info("Created new user %s" % user)

                return HttpResponseRedirect("/dashboard/")

            else:
                logger.error("Unable to register new user: username %s already exists." % form.cleaned_data['username'])
                return render_to_response('public/register.html', {'form': form, 'error': True}
                                          , context_instance=RequestContext(request))
        else:
            logger.debug("Registration form invalid. Returning for user %s to make corrections." % request.user)

    else:
        logger.debug("Returning blank registration form.")
        form = RegistrationForm()

    return render_to_response('public/register.html', {'form': form}, context_instance=RequestContext(request))
