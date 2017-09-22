import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from allianceauth.hooks import get_hooks
from .forms import FleetFormatterForm

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

    return render(request, 'services/fleetformattertool.html', context=context)


@login_required
def services_view(request):
    logger.debug("services_view called by user %s" % request.user)
    char = request.user.profile.main_character
    context = {'service_ctrls': []}
    for fn in get_hooks('services_hook'):
        # Render hooked services controls
        svc = fn()
        if svc.show_service_ctrl(request.user):
            context['service_ctrls'].append(svc.render_services_ctrl(request))

    return render(request, 'services/services.html', context=context)


def superuser_test(user):
    return user.is_superuser
