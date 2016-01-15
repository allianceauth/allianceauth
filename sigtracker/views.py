import datetime

from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test

from util import check_if_user_has_permission
from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager
from form import SignitureForm
from models import sigtracker

import logging

logger = logging.getLogger(__name__)

def sigtracker_util_test(user):
    return check_if_user_has_permission(user, 'member') or check_if_user_has_permission(user, 'blue_member')


@login_required
@user_passes_test(sigtracker_util_test)
@permission_required('auth.signiture_view')
def sigtracker_view(request):
    logger.debug("sigtracker_view called by user %s" % request.user)
    sigtracker_list = sigtracker.objects.all()
    render_items = {'sigtracker': sigtracker.objects.all()}

    return render_to_response('registered/signituremanagement.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.signiture_management')
def add_signiture_view(request):
    logger.debug("add_signiture_view called by user %s" % request.user)
    if request.method == 'POST':
        form = SignitureForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            # handle valid form
            sig = sigtracker()
            sig.ident = form.cleaned_data['ident']
            sig.system = form.cleaned_data['system']
            sig.destination = form.cleaned_data['destination']
            sig.sigtype = form.cleaned_data['sigtype']
            sig.status = form.cleaned_data['status']
            sig.notes = form.cleaned_data['notes']
            sig.save()
            return HttpResponseRedirect("/sigtracker/")
    else:
        logger.debug("Returning new SignitureForm")
        form = SignitureForm()

    render_items = {'form': form}

    return render_to_response('registered/addsigniture.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.signiture_management')
def remove_signiture(request, sigtracker_id):
    logger.debug("remove_signiture called by user %s for signiture id %s" % (request.user, sigtracker_id))
    if sigtracker.objects.filter(id=sigtracker_id).exists():
        sig = sigtracker.objects.get(id=sigtracker_id)
        sig.delete()
        logger.debug("Deleting sigtracker id %s by user %s" % (sigtracker_id, request.user))
    else:
        logger.error("Unable to delete signiture id %s for user %s - signiture matching id not found." % (sigtracker_id, request.user))
    return HttpResponseRedirect("/sigtracker/")
