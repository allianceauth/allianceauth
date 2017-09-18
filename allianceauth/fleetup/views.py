import datetime
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.template.defaulttags import register
from django.utils.translation import ugettext_lazy as _

from .managers import FleetUpManager

logger = logging.getLogger(__name__)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@login_required
@permission_required('auth.view_fleetup')
def fleetup_view(request):
    logger.debug("fleetup_view called by user %s" % request.user)

    operations_list = FleetUpManager.get_fleetup_operations()
    if operations_list is None:
        messages.add_message(request, messages.ERROR, _("Failed to get operations list, contact your administrator"))
        operations_list = {}
    timers_list = FleetUpManager.get_fleetup_timers()
    if timers_list is None:
        messages.add_message(request, messages.ERROR, _("Failed to get timers list, contact your administrator"))
        timers_list = {}
    now = datetime.datetime.now().strftime('%H:%M:%S')

    context = {"timers_list": sorted(timers_list.items()),
               "operations_list": sorted(operations_list.items()),
               "now": now}

    return render(request, 'fleetup/index.html', context=context)


@login_required
@permission_required('auth.human_resources')
@permission_required('auth.view_fleetup')
def fleetup_characters(request):
    logger.debug("fleetup_characters called by user %s" % request.user)

    member_list = FleetUpManager.get_fleetup_members()
    if member_list is None:
        messages.add_message(request, messages.ERROR, _("Failed to get member list, contact your administrator"))
        member_list = {}

    context = {"member_list": sorted(member_list.items())}

    return render(request, 'fleetup/characters.html', context=context)


@login_required
@permission_required('auth.view_fleetup')
def fleetup_fittings(request):
    logger.debug("fleetup_fittings called by user %s" % request.user)
    fitting_list = FleetUpManager.get_fleetup_fittings()

    if fitting_list is None:
        messages.add_message(request, messages.ERROR, _("Failed to get fitting list, contact your administrator"))
        fitting_list = {}

    context = {"fitting_list": sorted(fitting_list.items())}
    return render(request, 'fleetup/fittingsview.html', context=context)


@login_required
@permission_required('auth.view_fleetup')
def fleetup_fitting(request, fittingnumber):
    logger.debug("fleetup_fitting called by user %s" % request.user)
    fitting_eft = FleetUpManager.get_fleetup_fitting_eft(fittingnumber)
    fitting_data = FleetUpManager.get_fleetup_fitting(fittingnumber)
    doctrinenumber = FleetUpManager.get_fleetup_doctrineid(fittingnumber)
    doctrines_list = FleetUpManager.get_fleetup_doctrine(doctrinenumber)

    if fitting_eft is None or fitting_data is None or doctrinenumber is None:
        messages.add_message(request, messages.ERROR, _("There was an error getting some of the data for this fitting. "
                                                        "Contact your administrator"))

    context = {"fitting_eft": fitting_eft,
               "fitting_data": fitting_data,
               "doctrines_list": doctrines_list}
    return render(request, 'fleetup/fitting.html', context=context)


@login_required
@permission_required('auth.view_fleetup')
def fleetup_doctrines(request):
    logger.debug("fleetup_doctrines called by user %s" % request.user)
    doctrines_list = FleetUpManager.get_fleetup_doctrines()
    if doctrines_list is None:
        messages.add_message(request, messages.ERROR, _("Failed to get doctrines list, contact your administrator"))

    context = {"doctrines_list": doctrines_list}
    return render(request, 'fleetup/doctrinesview.html', context=context)


@login_required
@permission_required('auth.view_fleetup')
def fleetup_doctrine(request, doctrinenumber):
    logger.debug("fleetup_doctrine called by user %s" % request.user)
    doctrine = FleetUpManager.get_fleetup_doctrine(doctrinenumber)
    if doctrine is None:
        messages.add_message(request, messages.ERROR, _("Failed to get doctine, contact your administrator"))
    context = {"doctrine": doctrine}
    return render(request, 'fleetup/doctrine.html', context=context)
