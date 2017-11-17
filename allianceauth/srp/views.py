import logging
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from allianceauth.eveonline.providers import provider
from allianceauth.notifications import notify
from .form import SrpFleetMainForm
from .form import SrpFleetMainUpdateForm
from .form import SrpFleetUserRequestForm
from .models import SrpFleetMain
from .models import SrpUserRequest
from .managers import SRPManager

logger = logging.getLogger(__name__)


def random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


@login_required
@permission_required('srp.access_srp')
def srp_management(request, all=False):
    logger.debug("srp_management called by user %s" % request.user)
    fleets = SrpFleetMain.objects.select_related('fleet_commander').prefetch_related('srpuserrequest_set').all()
    if not all:
        fleets = fleets.filter(fleet_srp_status="")
    else:
        logger.debug("Returning all SRP requests")
    totalcost = fleets.aggregate(total_cost=Sum('srpuserrequest__srp_total_amount')).get('total_cost', 0)
    context = {"srpfleets": fleets, "totalcost": totalcost}
    return render(request, 'srp/management.html', context=context)

@login_required
@permission_required('srp.access_srp')
def srp_fleet_view(request, fleet_id):
    logger.debug("srp_fleet_view called by user %s for fleet id %s" % (request.user, fleet_id))
    try:
        fleet_main = SrpFleetMain.objects.get(id=fleet_id)
    except SrpFleetMain.DoesNotExist:
        raise Http404
    context = {"fleet_id": fleet_id, "fleet_status": fleet_main.fleet_srp_status,
               "srpfleetrequests": fleet_main.srpuserrequest_set.select_related('character').order_by('srp_ship_name'),
               "totalcost": fleet_main.total_cost}

    return render(request, 'srp/data.html', context=context)


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

    return render(request, 'srp/add.html', context=render_items)


@login_required
@permission_required('auth.srp_management')
def srp_fleet_remove(request, fleet_id):
    logger.debug("srp_fleet_remove called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.delete()
    logger.info("SRP Fleet %s deleted by user %s" % (srpfleetmain.fleet_name, request.user))
    messages.success(request, _('Removed SRP fleet %(fleetname)s.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("srp:management")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_disable(request, fleet_id):
    logger.debug("srp_fleet_disable called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.fleet_srp_code = ""
    srpfleetmain.save()
    logger.info("SRP Fleet %s disabled by user %s" % (srpfleetmain.fleet_name, request.user))
    messages.success(request, _('Disabled SRP fleet %(fleetname)s.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("srp:management")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_enable(request, fleet_id):
    logger.debug("srp_fleet_enable called by user %s for fleet id %s" % (request.user, fleet_id))
    srpfleetmain = get_object_or_404(SrpFleetMain, id=fleet_id)
    srpfleetmain.fleet_srp_code = random_string(8)
    srpfleetmain.save()
    logger.info("SRP Fleet %s enable by user %s" % (srpfleetmain.fleet_name, request.user))
    messages.success(request, _('Enabled SRP fleet %(fleetname)s.') % {"fleetname": srpfleetmain.fleet_name})
    return redirect("srp:management")


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
    return redirect("srp:fleet", fleet_id)


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
    return redirect("srp:fleet", fleet_id)


@login_required
@permission_required('srp.access_srp')
def srp_request_view(request, fleet_srp):
    logger.debug("srp_request_view called by user %s for fleet srp code %s" % (request.user, fleet_srp))

    if SrpFleetMain.objects.filter(fleet_srp_code=fleet_srp).exists() is False:
        logger.error("Unable to locate SRP Fleet using code %s for user %s" % (fleet_srp, request.user))
        messages.error(request,
                       _('Unable to locate SRP code with ID %(srpfleetid)s') % {"srpfleetid": fleet_srp})
        return redirect("srp:management")

    if request.method == 'POST':
        form = SrpFleetUserRequestForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())

        if form.is_valid():
            if SrpUserRequest.objects.filter(killboard_link=form.cleaned_data['killboard_link']).exists():
                messages.error(request,
                               _("This Killboard link has already been posted."))
                return redirect("srp:management")

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
                (ship_type_id, ship_value, victim_id) = SRPManager.get_kill_data(srp_kill_link)
            except ValueError:
                logger.debug("User %s Submitted Invalid Killmail Link %s or server could not be reached" % (
                    request.user, srp_request.killboard_link))
                # THIS SHOULD BE IN FORM VALIDATION
                messages.error(request,
                               _(
                                   "Your SRP request Killmail link is invalid. Please make sure you are using zKillboard."))
                return redirect("srp:management")

            if request.user.character_ownerships.filter(character__character_id=str(victim_id)).exists():
                srp_request.srp_ship_name = provider.get_itemtype(ship_type_id).name
                srp_request.kb_total_loss = ship_value
                srp_request.post_time = post_time
                srp_request.save()
                logger.info("Created SRP Request on behalf of user %s for fleet name %s" % (
                    request.user, srp_fleet_main.fleet_name))
                messages.success(request,
                                 _('Submitted SRP request for your %(ship)s.') % {"ship": srp_request.srp_ship_name})
                return redirect("srp:management")
            else:
                messages.error(request,
                               _(
                                   "Character %(charid)s does not belong to your Auth account. Please add the API key for this character and try again")
                               % {"charid": victim_id})
            return redirect("srp:management")
    else:
        logger.debug("Returning blank SrpFleetUserRequestForm")
        form = SrpFleetUserRequestForm()

    render_items = {'form': form}

    return render(request, 'srp/request.html', context=render_items)


@login_required
@permission_required('auth.srp_management')
def srp_request_remove(request):
    numrequests = len(request.POST) - 1
    logger.debug("srp_request_remove called by user %s for %s srp request id's" % (request.user, numrequests))
    stored_fleet_view = None
    for srp_request_id in request.POST:
        if numrequests == 0:
            messages.warning(request, _("No SRP requests selected"))
            return redirect("srp:management")
        if srp_request_id == "csrfmiddlewaretoken":
            continue
        if SrpUserRequest.objects.filter(id=srp_request_id).exists():
            srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
            stored_fleet_view = srpuserrequest.srp_fleet_main.id
            srpuserrequest.delete()
            logger.info("Deleted SRP request id %s for user %s" % (srp_request_id, request.user))
    if stored_fleet_view is None:
        logger.error("Unable to delete srp requests for user %s - request matching id not found." % (request.user))
        messages.error(request, _('Unable to locate selected SRP request.'))
        return redirect("srp:management")
    else:
        messages.success(request, _('Deleted %(numrequests)s SRP requests') % {"numrequests": numrequests})
        return redirect("srp:fleet", stored_fleet_view)


@login_required
@permission_required('auth.srp_management')
def srp_request_approve(request):
    numrequests = len(request.POST) - 1
    logger.debug("srp_request_approve called by user %s for %s srp request id's" % (request.user, numrequests))
    stored_fleet_view = None
    for srp_request_id in request.POST:
        if numrequests == 0:
            messages.warning(request, _("No SRP requests selected"))
            return redirect("srp:management")
        if srp_request_id == "csrfmiddlewaretoken":
            continue
        if SrpUserRequest.objects.filter(id=srp_request_id).exists():
            srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
            stored_fleet_view = srpuserrequest.srp_fleet_main.id
            srpuserrequest.srp_status = "Approved"
            if srpuserrequest.srp_total_amount == 0:
                srpuserrequest.srp_total_amount = srpuserrequest.kb_total_loss
            srpuserrequest.save()
            logger.info("Approved SRP request id %s for character %s by user %s" % (
                srp_request_id, srpuserrequest.character, request.user))
            notify(
                srpuserrequest.character.character_ownership.user,
                'SRP Request Approved',
                level='success',
                message='Your SRP request for a %s lost during %s has been approved for %s ISK.' % (
                    srpuserrequest.srp_ship_name, srpuserrequest.srp_fleet_main.fleet_name,
                    intcomma(srpuserrequest.srp_total_amount))
            )
    if stored_fleet_view is None:
        logger.error("Unable to approve srp request on behalf of user %s - request matching id not found." % (request.user))
        messages.error(request, _('Unable to locate selected SRP request.'))
        return redirect("srp:management")
    else:
        messages.success(request, _('Approved %(numrequests)s SRP requests') % {"numrequests": numrequests})
        return redirect("srp:fleet", stored_fleet_view)


@login_required
@permission_required('auth.srp_management')
def srp_request_reject(request):
    numrequests = len(request.POST) - 1
    logger.debug("srp_request_reject called by user %s for %s srp request id's" % (request.user, numrequests))
    stored_fleet_view = None
    for srp_request_id in request.POST:
        if numrequests == 0:
            messages.warning(request, _("No SRP requests selected"))
            return redirect("srp:management")
        if srp_request_id == "csrfmiddlewaretoken":
            continue
        if SrpUserRequest.objects.filter(id=srp_request_id).exists():
            srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
            stored_fleet_view = srpuserrequest.srp_fleet_main.id
            srpuserrequest.srp_status = "Rejected"
            srpuserrequest.save()
            logger.info("SRP request id %s for character %s rejected by %s" % (
                srp_request_id, srpuserrequest.character, request.user))
            notify(
                srpuserrequest.character.character_ownership.user,
                'SRP Request Rejected',
                level='danger',
                message='Your SRP request for a %s lost during %s has been rejected.' % (
                    srpuserrequest.srp_ship_name, srpuserrequest.srp_fleet_main.fleet_name)
            )
    if stored_fleet_view is None:
        logger.error("Unable to reject SRP request on behalf of user %s - request matching id not found." % (request.user))
        messages.error(request, _('Unable to locate selected SRP request'))
        return redirect("srp:management")
    else:
        messages.success(request, _('Rejected %(numrequests)s SRP requests.') % {"numrequests": numrequests})
        return redirect("srp:fleet", stored_fleet_view)


@login_required
@permission_required('auth.srp_management')
def srp_request_update_amount(request, fleet_srp_request_id):
    logger.debug("srp_request_update_amount called by user %s for fleet srp request id %s" % (
        request.user, fleet_srp_request_id))

    if SrpUserRequest.objects.filter(id=fleet_srp_request_id).exists() is False:
        logger.error("Unable to locate SRP request id %s for user %s" % (fleet_srp_request_id, request.user))
        messages.error(request,
                       _('Unable to locate SRP request with ID %(requestid)s') % {"requestid": fleet_srp_request_id})
        return redirect("srp:management")

    srp_request = SrpUserRequest.objects.get(id=fleet_srp_request_id)
    srp_request.srp_total_amount = request.POST['value']
    srp_request.save()
    logger.info("Updated srp request id %s total to %s by user %s" % (
        fleet_srp_request_id, request.POST['value'], request.user))
    return JsonResponse({"success": True, "pk": fleet_srp_request_id, "newValue": request.POST['value']})


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
            return redirect("srp:management")
    else:
        logger.debug("Returning blank SrpFleetMainUpdateForm")
        form = SrpFleetMainUpdateForm()
    return render(request, 'srp/update.html', context={'form': form})
