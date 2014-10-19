from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from models import GroupDescription
from models import GroupRequest

from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager


@login_required
@permission_required('auth.group_management')
def group_management(request):
    acceptrequests = []
    leaverequests = []

    for grouprequest in GroupRequest.objects.all():
        if grouprequest.leave_request:
            leaverequests.append(grouprequest)
        else:
            acceptrequests.append(grouprequest)

    render_items = {'acceptrequests': acceptrequests, 'leaverequests': leaverequests}

    return render_to_response('registered/groupmanagement.html',
                              render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.group_management')
def group_accept_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)
        group, created = Group.objects.get_or_create(name=group_request.group.name)
        request.user.groups.add(group)
        request.user.save()
        group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_reject_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)

        if group_request:
            group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_leave_accept_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)
        group, created = Group.objects.get_or_create(name=group_request.group.name)
        request.user.groups.remove(group)
        request.user.save()
        group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_leave_reject_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)

        if group_request:
            group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")

@login_required
def groups_view(request):

    paired_list = []

    for group in Group.objects.all():
        # Check if group is a corp
        if "Corp" in group.name:
            pass
        elif "AllianceMember" in group.name:
            pass
        else:
            # Get the descriptionn
            groupDesc = GroupDescription.objects.filter(group=group)
            groupRequest = GroupRequest.objects.filter(user=request.user).filter(group=group)

            if groupDesc:
                if groupRequest:
                    paired_list.append((group, groupDesc[0], groupRequest[0]))
                else:
                    paired_list.append((group, groupDesc[0], ""))
            else:
                if groupRequest:
                    paired_list.append((group, "", groupRequest[0]))
                else:
                    paired_list.append((group, "", ""))

    render_items = {'pairs': paired_list}
    return render_to_response('registered/groups.html',
                              render_items, context_instance=RequestContext(request))

@login_required
def group_request_add(request, group_id):
    auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
    grouprequest = GroupRequest()
    grouprequest.status = 'pending'
    grouprequest.group = Group.objects.get(id=group_id)
    grouprequest.user = request.user
    grouprequest.main_char = EveManager.get_character_by_id(auth_info.main_char_id)
    grouprequest.leave_request = False
    grouprequest.save()

    return HttpResponseRedirect("/groups")


@login_required
def group_request_leave(request, group_id):
    auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
    grouprequest = GroupRequest()
    grouprequest.status = 'pending'
    grouprequest.group = Group.objects.get(id=group_id)
    grouprequest.user = request.user
    grouprequest.main_char = EveManager.get_character_by_id(auth_info.main_char_id)
    grouprequest.leave_request = True
    grouprequest.save()

    return HttpResponseRedirect("/groups")