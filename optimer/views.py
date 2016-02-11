

from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.shortcuts import get_object_or_404

from util import check_if_user_has_permission
from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager
from form import opForm
from models import optimer
from form import optimerUpdateForm

import logging

logger = logging.getLogger(__name__)

def optimer_util_test(user):
    return check_if_user_has_permission(user, 'member') or check_if_user_has_permission(user, 'blue_member')


@login_required
@user_passes_test(optimer_util_test)
@permission_required('auth.optimer_view')
def optimer_view(request):
    logger.debug("optimer_view called by user %s" % request.user)
    optimer_list = optimer.objects.all()
    render_items = {'optimer': optimer.objects.all(),}

    return render_to_response('registered/operationmanagement.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.optimer_management')
def add_optimer_view(request):
    logger.debug("add_optimer_view called by user %s" % request.user)
    if request.method == 'POST':
    	form = opForm(request.POST)
    	logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            #Get Current Time
            post_time = timezone.now()
            # Get character
            auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
            character = EveManager.get_character_by_id(auth_info.main_char_id)
            # handle valid form
            op = optimer()
            op.doctrine = form.cleaned_data['doctrine']
            op.system = form.cleaned_data['system']
            op.location = form.cleaned_data['location']
            op.start = form.cleaned_data['start']
            op.duration = form.cleaned_data['duration']
            op.operation_name = form.cleaned_data['operation_name']
            op.fc = form.cleaned_data['fc']
            op.details = form.cleaned_data['details']
            op.create_time = post_time
            op.eve_character = character
            op.save()
            logger.info("User %s created op timer with name %s" % (request.user, op.operation_name))
            return HttpResponseRedirect("/optimer/")
    else:
        logger.debug("Returning new opForm")
        form = opForm()

    render_items = {'form': form}

    return render_to_response('registered/addoperation.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.optimer_management')
def remove_optimer(request, optimer_id):
    logger.debug("remove_optimer called by user %s for operation id %s" % (request.user, optimer_id))
    if optimer.objects.filter(id=optimer_id).exists():
        op = optimer.objects.get(id=optimer_id)
        op.delete()
        logger.info("Deleting optimer id %s by user %s" % (optimer_id, request.user))
    else:
        logger.error("Unable to delete optimer id %s for user %s - operation matching id not found." % (optimer_id, request.user))
    return HttpResponseRedirect("/optimer/")

@login_required
@permission_required('auth.optimer_management')
def edit_optimer(request, optimer_id):
    logger.debug("edit_optimer called by user %s for optimer id %s" % (request.user, optimer_id))
    op = get_object_or_404(optimer, id=optimer_id)
    if request.method == 'POST':
        form = optimerUpdateForm(request.POST)
        logger.debug("Received POST request containing update optimer form, is valid: %s" % form.is_valid())
        if form.is_valid():
            auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
            character = EveManager.get_character_by_id(auth_info.main_char_id)
            op.doctrine = form.cleaned_data['doctrine']
            op.system = form.cleaned_data['system']
            op.location = form.cleaned_data['location']
            op.start = form.cleaned_data['start']
            op.duration = form.cleaned_data['duration']
            op.operation_name = form.cleaned_data['operation_name']
            op.fc = form.cleaned_data['fc']
            op.details = form.cleaned_data['details']
            op.eve_character = character
            logger.info("User %s updating optimer id %s " % (request.user, optimer_id))
            op.save()

        logger.debug("Detected no changes between optimer id %s and supplied form." % optimer_id)
        return HttpResponseRedirect("/optimer/")
    else:
        data = {
            'doctrine': op.doctrine,
            'system': op.system,
            'location': op.location,
            'start': op.start,
            'duration': op.duration,
            'operation_name': op.operation_name,
            'fc': op.fc,
            'details': op.details,
            }
        form = optimerUpdateForm(initial= data)
    return render_to_response('registered/optimerupdate.html', {'form':form}, context_instance=RequestContext(request))
