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


def srp_util_test(user):
    return check_if_user_has_permission(user, 'member') or check_if_user_has_permission(user, 'blue_member')


@login_required
@user_passes_test(srp_util_test)
def srp_management(request):
    totalcost = 0
    runningcost = 0
    price_pair = {}
    for fleet_main in SrpFleetMain.objects.filter(fleet_srp_status="").iterator():
        for fleet_data in SrpUserRequest.objects.filter(srp_fleet_main=fleet_main).iterator():
            totalcost = totalcost + fleet_data.srp_total_amount
            runningcost = runningcost + fleet_data.srp_total_amount
        price_pair[fleet_main.id] = runningcost
        runningcost = 0

    context = {"srpfleets": SrpFleetMain.objects.filter(fleet_srp_status=""), "totalcost": totalcost,
               "price_pair": price_pair}
    return render_to_response('registered/srpmanagement.html', context, context_instance=RequestContext(request))


@login_required
@user_passes_test(srp_util_test)
def srp_management_all(request):
    totalcost = 0
    runningcost = 0
    price_pair = {}
    for fleet_main in SrpFleetMain.objects.all().iterator():
        for fleet_data in SrpUserRequest.objects.filter(srp_fleet_main=fleet_main).iterator():
            totalcost = totalcost + fleet_data.srp_total_amount
            runningcost = runningcost + fleet_data.srp_total_amount
        price_pair[fleet_main.id] = runningcost
        runningcost = 0

    context = {"srpfleets": SrpFleetMain.objects.all(), "totalcost": totalcost, "price_pair": price_pair}
    return render_to_response('registered/srpmanagement.html', context, context_instance=RequestContext(request))


@login_required
@user_passes_test(srp_util_test)
def srp_fleet_view(request, fleet_id):
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        fleet_main = SrpFleetMain.objects.get(id=fleet_id)
        totalcost = 0
        for fleet_data in SrpUserRequest.objects.filter(srp_fleet_main=fleet_main):
            totalcost = totalcost + fleet_data.srp_total_amount

        context = {"fleet_id": fleet_id, "fleet_status": fleet_main.fleet_srp_status,
                   "srpfleetrequests": SrpUserRequest.objects.filter(srp_fleet_main=fleet_main),
                   "totalcost": totalcost}

        return render_to_response('registered/srpfleetdata.html', context, context_instance=RequestContext(request))

    else:
        return HttpResponseRedirect("/srp")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_add_view(request):
    completed = False
    completed_srp_code = ""

    if request.method == 'POST':
        form = SrpFleetMainForm(request.POST)

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

    else:
        form = SrpFleetMainForm()

    render_items = {'form': form, "completed": completed, "completed_srp_code": completed_srp_code}

    return render_to_response('registered/srpfleetadd.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.srp_management')
def srp_fleet_remove(request, fleet_id):
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
        srpfleetmain.delete()

    return HttpResponseRedirect("/srp")


@login_required
@permission_required('auth.srp_management')
def srp_fleet_mark_completed(request, fleet_id):
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
        srpfleetmain.fleet_srp_status = "Completed"
        srpfleetmain.save()

    return HttpResponseRedirect("/srp_fleet_view/" + str(fleet_id))


@login_required
@permission_required('auth.srp_management')
def srp_fleet_mark_uncompleted(request, fleet_id):
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
        srpfleetmain.fleet_srp_status = ""
        srpfleetmain.save()

    return HttpResponseRedirect("/srp_fleet_view/" + str(fleet_id))


@login_required
@user_passes_test(srp_util_test)
def srp_request_view(request, fleet_srp):
    completed = False
    no_srp_code = False
    srp_code = ""

    if SrpFleetMain.objects.filter(fleet_srp_code=fleet_srp).exists() is False:
        no_srp_code = True

    if request.method == 'POST':
        form = SrpFleetUserRequestForm(request.POST)

        if form.is_valid():
            authinfo = AuthServicesInfoManager.get_auth_service_info(request.user)
            character = EveManager.get_character_by_id(authinfo.main_char_id)
            srp_fleet_main = SrpFleetMain.objects.get(fleet_srp_code=fleet_srp)

            srp_request = SrpUserRequest()
            srp_request.killboard_link = form.cleaned_data['killboard_link']
            srp_request.additional_info = form.cleaned_data['additional_info']
            srp_request.character = character
            srp_request.srp_fleet_main = srp_fleet_main
            srp_request.save()

            completed = True

    else:
        form = SrpFleetUserRequestForm()

    render_items = {'form': form, "completed": completed, "no_srp_code": no_srp_code}

    return render_to_response('registered/srpfleetrequest.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.srp_management')
def srp_request_remove(request, srp_request_id):
    stored_fleet_view = None

    if SrpUserRequest.objects.filter(id=srp_request_id).exists():
        srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
        stored_fleet_view = srpuserrequest.srp_fleet_main.id
        srpuserrequest.delete()

    if stored_fleet_view is None:
        return HttpResponseRedirect("/srp")
    else:
        return HttpResponseRedirect("/srp_fleet_view/" + str(stored_fleet_view))


@login_required
@permission_required('auth.srp_management')
def srp_request_approve(request, srp_request_id):
    stored_fleet_view = None

    if SrpUserRequest.objects.filter(id=srp_request_id).exists():
        srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
        stored_fleet_view = srpuserrequest.srp_fleet_main.id
        srpuserrequest.srp_status = "Approved"
        srpuserrequest.save()

    if stored_fleet_view is None:
        return HttpResponseRedirect("/srp")
    else:
        return HttpResponseRedirect("/srp_fleet_view/" + str(stored_fleet_view))


@login_required
@permission_required('auth.srp_management')
def srp_request_reject(request, srp_request_id):
    stored_fleet_view = None

    if SrpUserRequest.objects.filter(id=srp_request_id).exists():
        srpuserrequest = SrpUserRequest.objects.get(id=srp_request_id)
        stored_fleet_view = srpuserrequest.srp_fleet_main.id
        srpuserrequest.srp_status = "Rejected"
        srpuserrequest.save()

    if stored_fleet_view is None:
        return HttpResponseRedirect("/srp")
    else:
        return HttpResponseRedirect("/srp_fleet_view/" + str(stored_fleet_view))


@login_required
@permission_required('auth.srp_management')
def srp_request_update_amount_view(request, fleet_srp_request_id):
    no_srp_code = False
    srp_code = ""

    if SrpUserRequest.objects.filter(id=fleet_srp_request_id).exists() is False:
        no_srp_code = True

    if request.method == 'POST':
        form = SrpFleetUpdateCostForm(request.POST)

        if form.is_valid():
            srp_request = SrpUserRequest.objects.get(id=fleet_srp_request_id)
            srp_request.srp_total_amount = form.cleaned_data['srp_total_amount']
            srp_request.save()

            return HttpResponseRedirect("/srp_fleet_view/" + str(srp_request.srp_fleet_main.id))
    else:
        form = SrpFleetUpdateCostForm()

    render_items = {'form': form, "no_srp_code": no_srp_code}

    return render_to_response('registered/srpfleetrequestamount.html', render_items,
                              context_instance=RequestContext(request))


@login_required
@permission_required('auth.srp_management')
def srp_fleet_edit_view(request, fleet_id):
    no_fleet_id = False
    form = None
    if SrpFleetMain.objects.filter(id=fleet_id).exists():
        if request.method == 'POST':
            form = SrpFleetMainUpdateForm(request.POST)
            if form.is_valid():
                srpfleetmain = SrpFleetMain.objects.get(id=fleet_id)
                srpfleetmain.fleet_srp_aar_link = form.cleaned_data['fleet_aar_link']
                srpfleetmain.save()
                return HttpResponseRedirect("/srp")
        else:
            form = SrpFleetMainUpdateForm()
    else:
        no_fleet_id = True

    render_items = {'form': form, "no_fleet_id": no_fleet_id}

    return render_to_response('registered/srpfleetupdate.html', render_items,
                              context_instance=RequestContext(request))
