import datetime
from operator import itemgetter, attrgetter, methodcaller

from django.utils.timezone import utc

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import HttpResponseRedirect
from django.template.defaulttags import register
from django.contrib.humanize.templatetags.humanize import intword

from collections import namedtuple

from authentication.managers import AuthServicesInfoManager
from util import check_if_user_has_permission
from services.managers.eve_api_manager import EveApiManager
from services.managers.fleetup_manager import FleetUpManager
from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo
from eveonline.models import EveCharacter
from authentication.models import AuthServicesInfo

import logging

logger = logging.getLogger(__name__)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def fleetup_util_test(user):
    return check_if_user_has_permission(user, 'member') or check_if_user_has_permission(user, 'blue_member')

@login_required
@user_passes_test(fleetup_util_test)
def fleetup_view(request):
    logger.debug("fleetup_view called by user %s" % request.user)

    operations_list = FleetUpManager.get_fleetup_operations()
    timers_list = FleetUpManager.get_fleetup_timers()
    now = datetime.datetime.now().strftime('%H:%M:%S')

    context = {"timers_list": sorted(timers_list.items()),
               "operations_list": sorted(operations_list.items()),
               "now": now}

    return render_to_response('registered/fleetup.html',context, context_instance=RequestContext(request) )

@login_required
@permission_required('auth.human_resources')
def fleetup_characters(request):
    logger.debug("fleetup_characters called by user %s" % request.user)

    member_list = FleetUpManager.get_fleetup_members()

    context = {"member_list": sorted(member_list.items())}

    return render_to_response('registered/fleetupcharacters.html',context, context_instance=RequestContext(request) )

@login_required
@user_passes_test(fleetup_util_test)
def fleetup_fittings(request):
    logger.debug("fleetup_fittings called by user %s" % request.user)
    fitting_list = FleetUpManager.get_fleetup_fittings()
    context = {"fitting_list": sorted(fitting_list.items())}
    return render_to_response('registered/fleetupfittingsview.html',context, context_instance=RequestContext(request) )

@login_required
@user_passes_test(fleetup_util_test)
def fleetup_fitting(request, fittingnumber):
    logger.debug("fleetup_fitting called by user %s" % request.user)
    fitting_eft = FleetUpManager.get_fleetup_fitting_eft(fittingnumber)
    fitting_data = FleetUpManager.get_fleetup_fitting(fittingnumber)
    doctrinenumber = FleetUpManager.get_fleetup_doctrineid(fittingnumber)
    doctrines_list = FleetUpManager.get_fleetup_doctrine(doctrinenumber)
    context = {"fitting_eft": fitting_eft,
               "fitting_data": fitting_data,
               "doctrines_list": doctrines_list}
    return render_to_response('registered/fleetupfitting.html',context, context_instance=RequestContext(request) )


@login_required
@user_passes_test(fleetup_util_test)
def fleetup_doctrines(request):
    logger.debug("fleetup_doctrines called by user %s" % request.user)
    doctrines_list = FleetUpManager.get_fleetup_doctrines()
    context = {"doctrines_list": doctrines_list}
    return render_to_response('registered/fleetupdoctrinesview.html',context, context_instance=RequestContext(request) )

@login_required
@user_passes_test(fleetup_util_test)
def fleetup_doctrine(request, doctrinenumber):
    logger.debug("fleetup_doctrine called by user %s" % request.user)
    doctrine = FleetUpManager.get_fleetup_doctrine(doctrinenumber)
    context = {"doctrine": doctrine}
    return render_to_response('registered/fleetupdoctrine.html',context, context_instance=RequestContext(request) )

