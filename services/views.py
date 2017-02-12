from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from alliance_auth.hooks import get_hooks
from authentication.decorators import members_and_blues
from authentication.models import AuthServicesInfo
from eveonline.models import EveCharacter
from services.forms import FleetFormatterForm

import logging

logger = logging.getLogger(__name__)


@login_required
def fleet_formatter_view(request):
    logger.debug("fleet_formatter_view called by user %s" % request.user)
    generated = ""
    if request.method == 'POST':
        form = FleetFormatterForm(request.POST)
        logger.debug("Received POST request containing form, valid: %s" % form.is_valid())
        if form.is_valid():
            generated = "Fleet Name: " + form.cleaned_data['fleet_name'] + "\n"
            generated = generated + "FC: " + form.cleaned_data['fleet_commander'] + "\n"
            generated = generated + "Comms: " + form.cleaned_data['fleet_comms'] + "\n"
            generated = generated + "Fleet Type: " + form.cleaned_data['fleet_type'] + " || " + form.cleaned_data[
                'ship_priorities'] + "\n"
            generated = generated + "Form Up: " + form.cleaned_data['formup_location'] + " @ " + form.cleaned_data[
                'formup_time'] + "\n"
            generated = generated + "Duration: " + form.cleaned_data['expected_duration'] + "\n"
            generated = generated + "Reimbursable: " + form.cleaned_data['reimbursable'] + "\n"
            generated = generated + "Important: " + form.cleaned_data['important'] + "\n"
            if form.cleaned_data['comments'] != "":
                generated = generated + "Why: " + form.cleaned_data['comments'] + "\n"
            logger.info("Formatted fleet broadcast for user %s" % request.user)
    else:
        form = FleetFormatterForm()
        logger.debug("Returning empty form to user %s" % request.user)

    context = {'form': form, 'generated': generated}

    return render(request, 'registered/fleetformattertool.html', context=context)


@login_required
def services_view(request):
    logger.debug("services_view called by user %s" % request.user)
    auth = AuthServicesInfo.objects.get(user=request.user)
    char = None
    if auth.main_char_id:
        try:
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
        except EveCharacter.DoesNotExist:
            messages.warning(request, _("There's a problem with your main character. Please select a new one."))

    context = {'service_ctrls': []}
    for fn in get_hooks('services_hook'):
        # Render hooked services controls
        svc = fn()
        if svc.show_service_ctrl(request.user, auth.state):
            context['service_ctrls'].append(svc.render_services_ctrl(request))

    return render(request, 'registered/services.html', context=context)


def superuser_test(user):
    return user.is_superuser
