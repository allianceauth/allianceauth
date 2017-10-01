import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .form import OpForm

from .models import OpTimer

logger = logging.getLogger(__name__)


@login_required
@permission_required('auth.optimer_view')
def optimer_view(request):
    logger.debug("optimer_view called by user %s" % request.user)
    base_query = OpTimer.objects.select_related('eve_character')
    render_items = {'optimer': base_query.all(),
                    'future_timers': base_query.filter(
                        start__gte=timezone.now()),
                    'past_timers': base_query.filter(
                        start__lt=timezone.now()).order_by('-start')}

    return render(request, 'optimer/management.html', context=render_items)


@login_required
@permission_required('auth.optimer_management')
def add_optimer_view(request):
    logger.debug("add_optimer_view called by user %s" % request.user)
    if request.method == 'POST':
        form = OpForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            # Get Current Time
            post_time = timezone.now()
            # Get character
            character = request.user.profile.main_character
            # handle valid form
            op = OpTimer()
            op.doctrine = form.cleaned_data['doctrine']
            op.system = form.cleaned_data['system']
            op.start = form.cleaned_data['start']
            op.duration = form.cleaned_data['duration']
            op.operation_name = form.cleaned_data['operation_name']
            op.fc = form.cleaned_data['fc']
            op.create_time = post_time
            op.eve_character = character
            op.save()
            logger.info("User %s created op timer with name %s" % (request.user, op.operation_name))
            messages.success(request, _('Created operation timer for %(opname)s.') % {"opname": op.operation_name})
            return redirect("optimer:view")
    else:
        logger.debug("Returning new opForm")
        form = OpForm()

    render_items = {'form': form}

    return render(request, 'optimer/add.html', context=render_items)


@login_required
@permission_required('auth.optimer_management')
def remove_optimer(request, optimer_id):
    logger.debug("remove_optimer called by user %s for operation id %s" % (request.user, optimer_id))
    op = get_object_or_404(OpTimer, id=optimer_id)
    op.delete()
    logger.info("Deleting optimer id %s by user %s" % (optimer_id, request.user))
    messages.success(request, _('Removed operation timer for %(opname)s.') % {"opname": op.operation_name})
    return redirect("optimer:view")


@login_required
@permission_required('auth.optimer_management')
def edit_optimer(request, optimer_id):
    logger.debug("edit_optimer called by user %s for optimer id %s" % (request.user, optimer_id))
    op = get_object_or_404(OpTimer, id=optimer_id)
    if request.method == 'POST':
        form = OpForm(request.POST)
        logger.debug("Received POST request containing update optimer form, is valid: %s" % form.is_valid())
        if form.is_valid():
            character = request.user.profile.main_character
            op.doctrine = form.cleaned_data['doctrine']
            op.system = form.cleaned_data['system']
            op.start = form.cleaned_data['start']
            op.duration = form.cleaned_data['duration']
            op.operation_name = form.cleaned_data['operation_name']
            op.fc = form.cleaned_data['fc']
            op.eve_character = character
            logger.info("User %s updating optimer id %s " % (request.user, optimer_id))
            op.save()
            messages.success(request, _('Saved changes to operation timer for %(opname)s.') % {"opname": op.operation_name})
            return redirect("optimer:view")
    else:
        data = {
            'doctrine': op.doctrine,
            'system': op.system,
            'start': op.start,
            'duration': op.duration,
            'operation_name': op.operation_name,
            'fc': op.fc,
        }
        form = OpForm(initial=data)
    return render(request, 'optimer/update.html', context={'form': form})
