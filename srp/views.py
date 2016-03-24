from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test

from util import random_string
from eveonline.managers import EveManager
from authentication.managers import AuthServicesInfoManager
from util import check_if_user_has_permission
from models import SrpFleetMain
from models import SrpUserRequest
from form import SrpFleetMainForm
from form import SrpFleetUserRequestForm
from form import SrpFleetUpdateCostForm
from form import SrpFleetMainUpdateForm
from services.managers.srp_manager import srpManager
from notifications import notify

import logging

logger = logging.getLogger(__name__)

def srp_util_test(user):
    return check_if_user_has_permission(user, 'member') or check_if_user_has_permission(user, 'blue_member')


@login_required
@user_passes_test(srp_util_test)
def srp_management(request):
    logger.debug("srp_management called by user %s" % request.user)
    totalcost = 0
    runningcost = 0
    price_pair = {}
    for fleet_main in SrpFleetMain.objects.filter(fleet_srp_status="").iterator():
        for fleet_data in SrpUserRequest.objects.filter(srp_fleet_main=fleet_main).iterator():
            totalcost = totalcost + fleet_data.srp_total_amount
            runningcost = runningcost + fleet_data.srp_total_amount
        price_pair[fleet_main.id] = runningcost
        logger.debug("Determined SRP fleet %s costs %s" % (fleet_main.id, runningcost))
        runningcost = 0
    logger.debug("Determined total outstanding SRP cost %s" % totalcost)

    context = {"srpfleets": SrpFleetMain.objects.filter(fleet_srp_status=""), "totalcost": totalcost,
               "price_pair": price_pair}
    return render_to_response('registered/srpmanagement.html', context, context_instance=RequestContext(request))


@login_required
@user_passes_test(srp_util_test)
def srp_management_all(request):
    logger.debug("srp_management_all called by user %s" % request.user)
    totalcost = 0
    runningcost = 0
    price_pair = {}
    for fleet_main in SrpFleetMain.objects.all().iterator():
        for fleet_data in SrpUserRequest.objects.filter(srp_fleet_main=fleet_main).iterator():
            totalcost = totalcost + fleet_data.srp_total_amount
            runningcost = runningcost + fleet_data.srp_total_amount
        price_pair[fleet_main.id] = runningcost
        logger.debug("Determined SRP fleet %s costs %s" % (fleet_main.id, runningcost))
        runningcost = 0
    logger.debug("Determined all-time total SRP cost %s" % totalcost)

    context = {"srpfleets": SrpFleetMain.objects.all(), "totalcost": totalcost, "price_pair": price_pair}
    return render_to_response('registered/srpmanagement.html', context, context_instance=RequestContext(request))


@login_required
@user_passes_test(srp_util_test)
def srp_fleet_view(request, fleet_id):
    logger.debug("srp_fleet_view called by user %s for fleet id %s" % (request.user, fleet_id))
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        fleet_main = SrpFleetMain.objects.get(id=fleet_id)
        totalcost = 0
        for fleet_data in SrpUserRequest.objects.filter(srp_fleet_main=fleet_main):
            totalcost = totalcost + fleet_data.srp_total_amount
        logger.debug("Determiend fleet id %s total cost %s" % (fleet_id, totalcost))

        context = {"fleet_id": fleet_id, "fleet_status": fleet_main.fleet_srp_status,
                   "srpfleetrequests": SrpUserRequest.objects.filter(srp_fleet_main=fleet_main),
                   "totalcost": totalcost}

        return render_to_response('registered/srpfleetdata.html', context, context_instance=RequestContext(request))

    else:
        logger.error("Unable to view SRP fleet id %s for user %s - fleet matching id not found." % (fleet_id, request.user))
        return HttpResponseRedirect("/srp")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_add_view(request):
    logger.debug("srp_fleet_add_view called by user %s" % request.user)
    completed = False
    completed_srp_code = ""

    if request.method == 'POST':
        form = SrpFleetMainForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
            character = EveManager.get_character_by_id(authinfo.main_char_id)

            srp_fleet_main = SrpFleetMain()
            srp_fleet_main.fleet_name = form.cleaned_data['fleet_name']
            srp_fleet_main.fleet_doctrine = form.cleaned_data['fleet_doctrine']
            srp_fleet_main.fleet_time = form.cleaned_data['fleet_time']
            srp_fleet_main.fleet_srp_code = random_string(8)
            srp_fleet_main.fleet_commander = character

            srp_fleet_main.save()

            completed = True
            completed_srp_code = srp_fleet_main.fleet_srp_code
            logger.info("Created SRP Fleet %s by user %s" % (srp_fleet_main.fleet_name, request.user))

    else:
        logger.debug("Returning blank SrpFleetMainForm")
        form = SrpFleetMainForm()

    render_items = {'form': form, "completed": completed, "completed_srp_code": completed_srp_code}

    return render_to_response('registered/srpfleetadd.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.srp_management')
def srp_fleet_remove(request, fleet_id):
    logger.debug("srp_fleet_remove called by user %s for fleet id %s" % (request.user, fleet_id))
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
        srpfleetmain.delete()
        logger.info("SRP Fleet %s deleted by user %s" % (srpfleetmain.fleet_name, request.user))
    else:
        logger.error("Unable to delete SRP fleet id %s for user %s - fleet matching id not found." % (fleet_id, request.user))
    return HttpResponseRedirect("/srp")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_mark_completed(request, fleet_id):
    logger.debug("srp_fleet_mark_completed called by user %s for fleet id %s" % (request.user, fleet_id))
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
        srpfleetmain.fleet_srp_status = "Completed"
        srpfleetmain.save()
        logger.info("Marked SRP Fleet %s as completed by user %s" % (srpfleetmain.fleet_name, request.user))
    else:
        logger.error("Unable to mark SRP fleet with id %s as completed for user %s - fleet matching id not found." % (fleet_id, request.user))
    return HttpResponseRedirect("/srp_fleet_view/" + str(fleet_id))


@login_required
@permission_required('auth.srp_management')
def srp_fleet_mark_uncompleted(request, fleet_id):
    logger.debug("srp_fleet_mark_uncompleted called by user %s for fleet id %s" % (request.user, fleet_id))
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
        srpfleetmain.fleet_srp_status = ""
        srpfleetmain.save()
        logger.info("Marked SRP Fleet %s as incomplete for user %s" % (fleet_id, request.user))
    else:
        logger.error("Unable to mark SRP Fleet id %s as incomplete for user %s - fleet matching id not found." % (fleet_id, request.user))
    return HttpResponseRedirect("/srp_fleet_view/" + str(fleet_id))


@login_required
@user_passes_test(srp_util_test)
def srp_request_view(request, fleet_srp):
    logger.debug("srp_request_view called by user %s for fleet srp code %s" % (request.user, fleet_srp))
    completed = False
    no_srp_code = False
    srp_code = ""

    if SrpFleetMain.objects.filter(fleet_srp_code=fleet_srp).exists() is False:
        no_srp_code = True
        logger.error("Unable to locate SRP Fleet using code %s for user %s" % (fleet_srp, request.user))

    if request.method == 'POST':
        form = SrpFleetUserRequestForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())

        if form.is_valid():
            authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
            character = EveManager.get_character_by_id(authinfo.main_char_id)
            srp_fleet_main = SrpFleetMain.objects.get(fleet_srp_code=fleet_srp)


            srp_request = SrpUserRequest()
            srp_request.killboard_link = form.cleaned_data['killboard_link']
            srp_request.additional_info = form.cleaned_data['additional_info']
            srp_request.character = character
            srp_request.srp_fleet_main = srp_fleet_main

            try:
                srp_kill_link = srpManager.get_kill_id(srp_request.killboard_link)
                (srp_kill_data, ship_value) = srpManager.get_kill_data(srp_kill_link)
            except:
                logger.debug("User %s Submitted Invalid Killmail Link %s or server could not be reached" % (request.user, srp_request.killboard_link))
                notify(request.user, "Your SRP request Killmail Link Failed Validation", message="Your SRP request Killmail link %s is invalid. Please make sure your using zKillboard." % srp_request.killboard_link, level="danger")
                return HttpResponseRedirect("/srp")
            srp_ship_name = srpManager.get_ship_name(srp_kill_data)
            srp_request.srp_ship_name = srp_ship_name
            kb_total_loss = ship_value
            srp_request.kb_total_loss = kb_total_loss
            srp_request.save()
            completed = True
            logger.info("Created SRP Request on behalf of user %s for fleet name %s" % (request.user, srp_fleet_main.fleet_name))

    else:
        logger.debug("Returning blank SrpFleetUserRequestForm")
        form = SrpFleetUserRequestForm()

    render_items = {'form': form, "completed": completed, "no_srp_code": no_srp_code}

    return render_to_response('registered/srpfleetrequest.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.srp_management')
def srp_request_remove(request, srp_request_id):
    logger.debug("srp_request_remove called by user %s for srp request id %s" % (request.user, srp_request_id))
    stored_fleet_view = None

    if SrpUserRequest.objects.filter(id=srp_request_id).exists():
        srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
        stored_fleet_view = srpuserrequest.srp_fleet_main.id
        srpuserrequest.delete()
        logger.info("Deleted SRP request id %s for user %s" % (srp_request_id, request.user))

    if stored_fleet_view is None:
        logger.error("Unable to delete srp request id %s for user %s - request matching id not found." % (srp_request_id, request.user))
        return HttpResponseRedirect("/srp")
    else:
        return HttpResponseRedirect("/srp_fleet_view/" + str(stored_fleet_view))


@login_required
@permission_required('auth.srp_management')
def srp_request_approve(request, srp_request_id):
    logger.debug("srp_request_approve called by user %s for srp request id %s" % (request.user, srp_request_id))
    stored_fleet_view = None

    if SrpUserRequest.objects.filter(id=srp_request_id).exists():
        srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
        stored_fleet_view = srpuserrequest.srp_fleet_main.id
        srpuserrequest.srp_status = "Approved"
        srpuserrequest.save()
        logger.info("Approved SRP request id %s for character %s by user %s" % (srp_request_id, srpuserrequest.character, request.user))
    if stored_fleet_view is None:
        logger.error("Unable to approve srp request id %s on behalf of user %s - request matching id not found." % (srp_request_id, request.user))
        return HttpResponseRedirect("/srp")
    else:
        return HttpResponseRedirect("/srp_fleet_view/" + str(stored_fleet_view))


@login_required
@permission_required('auth.srp_management')
def srp_request_reject(request, srp_request_id):
    logger.debug("srp_request_reject called by user %s for srp request id %s" % (request.user, srp_request_id))
    stored_fleet_view = None

    if SrpUserRequest.objects.filter(id=srp_request_id).exists():
        srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
        stored_fleet_view = srpuserrequest.srp_fleet_main.id
        srpuserrequest.srp_status = "Rejected"
        srpuserrequest.save()
        logger.info("SRP request id %s for character %s rejected by %s" % (srp_request_id, srpuserrequest.character, request.user))

    if stored_fleet_view is None:
        logger.error("Unable to reject SRP request id %s on behalf of user %s - request matching id not found." % (srp_request_id, request.user))
        return HttpResponseRedirect("/srp")
    else:
        return HttpResponseRedirect("/srp_fleet_view/" + str(stored_fleet_view))


@login_required
@permission_required('auth.srp_management')
def srp_request_update_amount_view(request, fleet_srp_request_id):
    logger.debug("srp_request_update_amount_view called by user %s for fleet srp request id %s" % (request.user, fleet_srp_request_id))
    no_srp_code = False
    srp_code = ""

    if SrpUserRequest.objects.filter(id=fleet_srp_request_id).exists() is False:
        logger.error("Unable to locate SRP request id %s for user %s" % (fleet_srp_request_id, request.user))
        no_srp_code = True

    if request.method == 'POST':
        form = SrpFleetUpdateCostForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            srp_request = SrpUserRequest.objects.get(id=fleet_srp_request_id)
            srp_request.srp_total_amount = form.cleaned_data['srp_total_amount']
            srp_request.save()
            logger.info("Updated srp request id %s total to %s by user %s" % (fleet_srp_request_id, form.cleaned_data['srp_total_amount'], request.user))

            return HttpResponseRedirect("/srp_fleet_view/" + str(srp_request.srp_fleet_main.id))
    else:
        logger.debug("Returning blank SrpFleetUpdateCostForm")
        form = SrpFleetUpdateCostForm()

    render_items = {'form': form, "no_srp_code": no_srp_code}

    return render_to_response('registered/srpfleetrequestamount.html', render_items,
                              context_instance=RequestContext(request))


@login_required
@permission_required('auth.srp_management')
def srp_fleet_edit_view(request, fleet_id):
    logger.debug("srp_fleet_edit_view called by user %s for fleet id %s" % (request.user, fleet_id))
    no_fleet_id = False
    form = None
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        if request.method == 'POST':
            form = SrpFleetMainUpdateForm(request.POST)
            logger.debug("Request type POST contains form valid: %s" % form.is_valid())
            if form.is_valid():
                srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
                srpfleetmain.fleet_srp_aar_link = form.cleaned_data['fleet_aar_link']
                srpfleetmain.save()
                logger.info("User %s edited SRP Fleet %s" % (request.user, srpfleetmain.fleet_name))
                return HttpResponseRedirect("/srp")
        else:
            logger.debug("Returning blank SrpFleetMainUpdateForm")
            form = SrpFleetMainUpdateForm()
    else:
        logger.error("Unable to edit srp fleet id %s for user %s - fleet matching id not found." % (fleet_id, request.user))
        no_fleet_id = True

    render_items = {'form': form, "no_fleet_id": no_fleet_id}

    return render_to_response('registered/srpfleetupdate.html', render_items,
                              context_instance=RequestContext(request))
