from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import AuthServicesInfo
from eveonline.managers import EveManager
from optimer.form import opForm
from optimer.models import optimer
from authentication.decorators import members_and_blues

import logging

logger = logging.getLogger(__name__)


@login_required
@members_and_blues()
@permission_required('auth.optimer_view')
def optimer_view(request):
    logger.debug("optimer_view called by user %s" % request.user)
    render_items = {'optimer': optimer.objects.all(), }

    return render(request, 'registered/operationmanagement.html', context=render_items)


@login_required
@permission_required('auth.optimer_management')
def add_optimer_view(request):
    logger.debug("add_optimer_view called by user %s" % request.user)
    if request.method == 'POST':
        form = opForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            # Get Current Time
            post_time = timezone.now()
            # Get character
            auth_info = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
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
            messages.success(request, 'Created operation timer for %s.' % op.operation_name)
            return redirect("/optimer/")
    else:
        logger.debug("Returning new opForm")
        form = opForm()

    render_items = {'form': form}

    return render(request, 'registered/addoperation.html', context=render_items)


@login_required
@permission_required('auth.optimer_management')
def remove_optimer(request, optimer_id):
    logger.debug("remove_optimer called by user %s for operation id %s" % (request.user, optimer_id))
    if optimer.objects.filter(id=optimer_id).exists():
        op = optimer.objects.get(id=optimer_id)
        op.delete()
        logger.info("Deleting optimer id %s by user %s" % (optimer_id, request.user))
        messages.success(request, 'Removed operation timer for %s.' % op.operation_name)
    else:
        logger.error("Unable to delete optimer id %s for user %s - operation matching id not found." % (
            optimer_id, request.user))
    return redirect("auth_optimer_view")


@login_required
@permission_required('auth.optimer_management')
def edit_optimer(request, optimer_id):
    logger.debug("edit_optimer called by user %s for optimer id %s" % (request.user, optimer_id))
    op = get_object_or_404(optimer, id=optimer_id)
    if request.method == 'POST':
        form = opForm(request.POST)
        logger.debug("Received POST request containing update optimer form, is valid: %s" % form.is_valid())
        if form.is_valid():
            auth_info = AuthServicesInfo.objects.get_or_create(user=request.user)[0]
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
            messages.success(request, 'Saved changes to operation timer for %s.' % op.operation_name)
            return redirect("auth_optimer_view")
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
        form = opForm(initial=data)
    return render(request, 'registered/optimerupdate.html', context={'form': form})
