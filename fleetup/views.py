from __future__ import unicode_literals
import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.template.defaulttags import register
from services.managers.fleetup_manager import FleetUpManager
from authentication.decorators import members_and_blues

import logging

logger = logging.getLogger(__name__)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@login_required
@members_and_blues()
def fleetup_view(request):
    logger.debug("fleetup_view called by user %s" % request.user)

    operations_list = FleetUpManager.get_fleetup_operations()
    timers_list = FleetUpManager.get_fleetup_timers()
    now = datetime.datetime.now().strftime('%H:%M:%S')

    context = {"timers_list": sorted(timers_list.items()),
               "operations_list": sorted(operations_list.items()),
               "now": now}

    return render(request, 'registered/fleetup.html', context=context)


@login_required
@permission_required('auth.human_resources')
def fleetup_characters(request):
    logger.debug("fleetup_characters called by user %s" % request.user)

    member_list = FleetUpManager.get_fleetup_members()

    context = {"member_list": sorted(member_list.items())}

    return render(request, 'registered/fleetupcharacters.html', context=context)


@login_required
@members_and_blues()
def fleetup_fittings(request):
    logger.debug("fleetup_fittings called by user %s" % request.user)
    fitting_list = FleetUpManager.get_fleetup_fittings()
    context = {"fitting_list": sorted(fitting_list.items())}
    return render(request, 'registered/fleetupfittingsview.html', context=context)


@login_required
@members_and_blues()
def fleetup_fitting(request, fittingnumber):
    logger.debug("fleetup_fitting called by user %s" % request.user)
    fitting_eft = FleetUpManager.get_fleetup_fitting_eft(fittingnumber)
    fitting_data = FleetUpManager.get_fleetup_fitting(fittingnumber)
    doctrinenumber = FleetUpManager.get_fleetup_doctrineid(fittingnumber)
    doctrines_list = FleetUpManager.get_fleetup_doctrine(doctrinenumber)
    context = {"fitting_eft": fitting_eft,
               "fitting_data": fitting_data,
               "doctrines_list": doctrines_list}
    return render(request, 'registered/fleetupfitting.html', context=context)


@login_required
@members_and_blues()
def fleetup_doctrines(request):
    logger.debug("fleetup_doctrines called by user %s" % request.user)
    doctrines_list = FleetUpManager.get_fleetup_doctrines()
    context = {"doctrines_list": doctrines_list}
    return render(request, 'registered/fleetupdoctrinesview.html', context=context)


@login_required
@members_and_blues()
def fleetup_doctrine(request, doctrinenumber):
    logger.debug("fleetup_doctrine called by user %s" % request.user)
    doctrine = FleetUpManager.get_fleetup_doctrine(doctrinenumber)
    context = {"doctrine": doctrine}
    return render(request, 'registered/fleetupdoctrine.html', context=context)
