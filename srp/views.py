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


def srp_util_test(user):
    return check_if_user_has_permission(user, 'alliance_member') or check_if_user_has_permission(user, 'blue_member')


@login_required
@user_passes_test(srp_util_test)
def srp_management(request):
    context = {"srpfleets": SrpFleetMain.objects.all()}
    return render_to_response('registered/srpmanagement.html', context, context_instance=RequestContext(request))


@login_required
@user_passes_test(srp_util_test)
def srp_fleet_view(request, fleet_id):
    if SrpFleetMain.objects.filter(id=fleet_id):
        fleet_main = SrpFleetMain.objects.get(id=fleet_id)
        context = {"srpfleetrequests": SrpUserRequest.objects.filter(srp_fleet_main=fleet_main)}

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