from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from eveonline.managers import EveManager
from srp.models import SrpFleetMain
from srp.models import SrpUserRequest
from srp.form import SrpFleetMainForm
from srp.form import SrpFleetUserRequestForm
from srp.form import SrpFleetUpdateCostForm
from srp.form import SrpFleetMainUpdateForm
from srp.managers import SRPManager
from notifications import notify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.humanize.templatetags.humanize import intcomma
import uuid

import logging

logger = logging.getLogger(__name__)


def random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


@login_required
@permission_required('srp.access_srp')
def srp_management(request):
    logger.debug("srp_management called by user %s" % request.user)
    fleets = SrpFleetMain.objects.filter(fleet_srp_status="")
    totalcost = sum([int(fleet.total_cost) for fleet in fleets])
    context = {"srpfleets": fleets, "totalcost": totalcost}
    return render(request, 'registered/srpmanagement.html', context=context)


@login_required
@permission_required('srp.access_srp')
def srp_management_all(request):
    logger.debug("srp_management_all called by user %s" % request.user)
    fleets = SrpFleetMain.objects.all()
    totalcost = sum([int(fleet.total_cost) for fleet in fleets])
    context = {"srpfleets": SrpFleetMain.objects.all(), "totalcost": totalcost}
    return render(request, 'registered/srpmanagement.html', context=context)


@login_required
@permission_required('srp.access_srp')
def srp_fleet_view(request, fleet_id):
    logger.debug("srp_fleet_view called by user %s for fleet id %s" % (request.user, fleet_id))
    fleet_main = get_object_or_404(SrpFleetMain, id=fleet_id)
    context = {"fleet_id": fleet_id, "fleet_status": fleet_main.fleet_srp_status,
               "srpfleetrequests": fleet_main.srpuserrequest_set.all(),
               "totalcost": fleet_main.total_cost}

    return render(request, 'registered/srpfleetdata.html', context=context)


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
            srp_fleet_main = SrpFleetMain()
            srp_fleet_main.fleet_name = form.cleaned_data['fleet_name']
            srp_fleet_main.fleet_doctrine = form.cleaned_data['fleet_doctrine']
            srp_fleet_main.fleet_time = form.cleaned_data['fleet_time']
            srp_fleet_main.fleet_srp_code = random_string(8)
            srp_fleet_main.fleet_commander = request.user.profile.main_character

            srp_fleet_main.save()

            completed = True
            completed_srp_code = srp_fleet_main.fleet_srp_code
            logger.info("Created SRP Fleet %s by user %s" % (srp_fleet_main.fleet_name, request.user))
            messages.success(request, _('Created SRP fleet %(fleetname)s.') % {"fleetname": srp_fleet_main.fleet_name})

    else:
        logger.debug("Returning blank SrpFleetMainForm")
        form = SrpFleetMainForm()

    render_items = {'form': form, "completed": completed, "completed_srp_code": completed_srp_code}

    return render(request, 'registered/srpfleetadd.html', context=render_items)


@login_required
@permission_required('auth.srp_management')
def srp_fleet_remove(request, fleet_id):
    logger.debug("srp_fleet_remove called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.delete()
    logger.info("SRP Fleet %s deleted by user %s" % (srpfleetmain.fleet_name, request.user))
    messages.success(request, _('Removed SRP fleet %(fleetname)s.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("auth_srp_management_view")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_disable(request, fleet_id):
    logger.debug("srp_fleet_disable called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.fleet_srp_code = ""
    srpfleetmain.save()
    logger.info("SRP Fleet %s disabled by user %s" % (srpfleetmain.fleet_name, request.user))
    messages.success(request, _('Disabled SRP fleet %(fleetname)s.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("auth_srp_management_view")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_enable(request, fleet_id):
    logger.debug("srp_fleet_enable called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.fleet_srp_code = random_string(8)
    srpfleetmain.save()
    logger.info("SRP Fleet %s enable by user %s" % (srpfleetmain.fleet_name, request.user))
    messages.success(request, _('Enabled SRP fleet %(fleetname)s.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("auth_srp_management_view")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_mark_completed(request, fleet_id):
    logger.debug("srp_fleet_mark_completed called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.fleet_srp_status = "Completed"
    srpfleetmain.save()
    logger.info("Marked SRP Fleet %s as completed by user %s" % (srpfleetmain.fleet_name, request.user))
    messages.success(request,
                     _('Marked SRP fleet %(fleetname)s as completed.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("auth_srp_fleet_view", fleet_id)


@login_required
@permission_required('auth.srp_management')
def srp_fleet_mark_uncompleted(request, fleet_id):
    logger.debug("srp_fleet_mark_uncompleted called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.fleet_srp_status = ""
    srpfleetmain.save()
    logger.info("Marked SRP Fleet %s as incomplete for user %s" % (fleet_id, request.user))
    messages.success(request,
                     _('Marked SRP fleet %(fleetname)s as incomplete.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("auth_srp_fleet_view", fleet_id)


@login_required
@permission_required('srp.access_srp')
def srp_request_view(request, fleet_srp):
    logger.debug("srp_request_view called by user %s for fleet srp code %s" % (request.user, fleet_srp))

    if SrpFleetMain.objects.filter(fleet_srp_code=fleet_srp).exists() is False:
        messages.error(request, _("Unable to locate SRP Fleet using code %(code)s") % fleet_srp)
        return redirect(srp_management)

    if request.method == 'POST':
        form = SrpFleetUserRequestForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())

        if form.is_valid():
            character = request.user.profile.main_character
            srp_fleet_main = SrpFleetMain.objects.get(fleet_srp_code=fleet_srp)
            post_time = timezone.now()

            srp_request = SrpUserRequest()
            srp_request.killboard_link = form.cleaned_data['killboard_link']
            srp_request.additional_info = form.cleaned_data['additional_info']
            srp_request.character = character
            srp_request.srp_fleet_main = srp_fleet_main

            try:
                srp_kill_link = SRPManager.get_kill_id(srp_request.killboard_link)
                (ship_type_id, ship_value) = SRPManager.get_kill_data(srp_kill_link)
            except ValueError:
                logger.debug("User %s Submitted Invalid Killmail Link %s or server could not be reached" % (
                    request.user, srp_request.killboard_link))
                # THIS SHOULD BE IN FORM VALIDATION
                messages.error(request,
                               _(
                                   "Your SRP request Killmail link is invalid. Please make sure you are using zKillboard."))
                return redirect("auth_srp_management_view")
            srp_ship_name = EveManager.get_itemtype(ship_type_id).name
            srp_request.srp_ship_name = srp_ship_name
            kb_total_loss = ship_value
            srp_request.kb_total_loss = kb_total_loss
            srp_request.post_time = post_time
            srp_request.save()
            logger.info("Created SRP Request on behalf of user %s for fleet name %s" % (
                request.user, srp_fleet_main.fleet_name))
            messages.success(request, _('Submitted SRP request for your %(ship)s.') % {"ship": srp_ship_name})
            return redirect(srp_management)

    else:
        logger.debug("Returning blank SrpFleetUserRequestForm")
        form = SrpFleetUserRequestForm()

    render_items = {'form': form}

    return render(request, 'registered/srpfleetrequest.html', context=render_items)


@login_required
@permission_required('auth.srp_management')
def srp_request_remove(request, srp_request_id):
    logger.debug("srp_request_remove called by user %s for srp request id %s" % (request.user, srp_request_id))

    srpuserrequest = get_object_or_404(SrpUserRequest, id=srp_request_id)
    srpuserrequest.delete()
    logger.info("Deleted SRP request id %s for user %s" % (srp_request_id, request.user))
    messages.success(request, _('Deleted SRP request from %(character)s for their %(ship)s.') % {
        "character": srpuserrequest.character, "ship": srpuserrequest.srp_ship_name})
    return redirect("auth_srp_fleet_view", srpuserrequest.srp_fleet_main.id)


@login_required
@permission_required('auth.srp_management')
def srp_request_approve(request, srp_request_id):
    logger.debug("srp_request_approve called by user %s for srp request id %s" % (request.user, srp_request_id))
    srpuserrequest = get_object_or_404(SrpUserRequest, id=srp_request_id)
    srpuserrequest.srp_status = "Approved"
    if srpuserrequest.srp_total_amount == 0:
        srpuserrequest.srp_total_amount = srpuserrequest.kb_total_loss
    srpuserrequest.save()
    logger.info("Approved SRP request id %s for character %s by user %s" % (
        srp_request_id, srpuserrequest.character, request.user))
    messages.success(request, _('Approved SRP request from %(character)s for their %(ship)s.') % {
        "character": srpuserrequest.character, "ship": srpuserrequest.srp_ship_name})
    if srpuserrequest.character.userprofile:
        notify(
            srpuserrequest.character.userprofile.user,
            'SRP Request Approved',
            level='success',
            message='Your SRP request for a %s lost during %s has been approved for %s ISK.' % (
                srpuserrequest.srp_ship_name, srpuserrequest.srp_fleet_main.fleet_name,
                intcomma(srpuserrequest.srp_total_amount))
        )
    return redirect("auth_srp_fleet_view", srpuserrequest.srp_fleet_main.id)


@login_required
@permission_required('auth.srp_management')
def srp_request_reject(request, srp_request_id):
    logger.debug("srp_request_reject called by user %s for srp request id %s" % (request.user, srp_request_id))
    srpuserrequest = get_object_or_404(SrpUserRequest, id=srp_request_id)
    srpuserrequest.srp_status = "Rejected"
    srpuserrequest.save()
    logger.info("SRP request id %s for character %s rejected by %s" % (
        srp_request_id, srpuserrequest.character, request.user))
    messages.success(request, _('Rejected SRP request from %(character)s for their %(ship)s.') % {
        "character": srpuserrequest.character, "ship": srpuserrequest.srp_ship_name})
    if srpuserrequest.character.userprofile:
        notify(
            srpuserrequest.character.userprofile.user,
            'SRP Request Rejected',
            level='danger',
            message='Your SRP request for a %s lost during %s has been rejected.' % (
                srpuserrequest.srp_ship_name, srpuserrequest.srp_fleet_main.fleet_name)
        )
    return redirect("auth_srp_fleet_view", srpuserrequest.srp_fleet_main.id)


@login_required
@permission_required('auth.srp_management')
def srp_request_update_amount_view(request, fleet_srp_request_id):
    logger.debug("srp_request_update_amount_view called by user %s for fleet srp request id %s" % (
        request.user, fleet_srp_request_id))

    srp_request = get_object_or_404(SrpUserRequest, id=fleet_srp_request_id)
    if request.method == 'POST':
        form = SrpFleetUpdateCostForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            srp_request.srp_total_amount = form.cleaned_data['srp_total_amount']
            srp_request.save()
            logger.info("Updated srp request id %s total to %s by user %s" % (
                fleet_srp_request_id, intcomma(form.cleaned_data['srp_total_amount']), request.user))
            messages.success(request, _('Updated SRP amount.'))
            return redirect("auth_srp_fleet_view", srp_request.srp_fleet_main.id)
    else:
        logger.debug("Returning blank SrpFleetUpdateCostForm")
        form = SrpFleetUpdateCostForm(initial={'srp_total_amount': srp_request.srp_total_amount or srp_request.kb_total_loss})

    render_items = {'form': form}

    return render(request, 'registered/srpfleetrequestamount.html', context=render_items)


@login_required
@permission_required('auth.srp_management')
def srp_fleet_edit_view(request, fleet_id):
    logger.debug("srp_fleet_edit_view called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    if request.method == 'POST':
        form = SrpFleetMainUpdateForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            srpfleetmain.fleet_srp_aar_link = form.cleaned_data['fleet_aar_link']
            srpfleetmain.save()
            logger.info("User %s edited SRP Fleet %s" % (request.user, srpfleetmain.fleet_name))
            messages.success(request,
                             _('Saved changes to SRP fleet %(fleetname)s') % {"fleetname": srpfleetmain.fleet_name})
            return redirect("auth_srp_management_view")
    else:
        logger.debug("Returning blank SrpFleetMainUpdateForm")
        form = SrpFleetMainUpdateForm()
    return render(request, 'registered/srpfleetupdate.html', context={'form': form})
