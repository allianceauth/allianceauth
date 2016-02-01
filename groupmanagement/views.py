from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from models import GroupDescription
from models import GroupRequest
from models import HiddenGroup
from models import OpenGroup
from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager

import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('auth.group_management')
def group_management(request):
    logger.debug("group_management called by user %s" % request.user)
    acceptrequests = []
    leaverequests = []

    for grouprequest in GroupRequest.objects.all():
        if grouprequest.leave_request:
            leaverequests.append(grouprequest)
        else:
            acceptrequests.append(grouprequest)
    logger.debug("Providing user %s with %s acceptrequests and %s leaverequests." % (request.user, len(acceptrequests), len(leaverequests)))

    render_items = {'acceptrequests': acceptrequests, 'leaverequests': leaverequests}

    return render_to_response('registered/groupmanagement.html',
                              render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.group_management')
def group_accept_request(request, group_request_id):
    logger.debug("group_accept_request called by user %s for grouprequest id %s" % (request.user, group_request_id))
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)
        group, created = Group.objects.get_or_create(name=group_request.group.name)
        group_request.user.groups.add(group)
        group_request.user.save()
        group_request.delete()
        logger.info("User %s accepted group request from user %s to group %s" % (request.user, group_request.user, group_request.group.name))
    except:
        logger.exception("Unhandled exception occured while user %s attempting to accept grouprequest id %s." % (request.user, group_request_id))
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_reject_request(request, group_request_id):
    logger.debug("group_reject_request called by user %s for group request id %s" % (request.user, group_request_id))
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)

        if group_request:
            logger.info("User %s rejected group request from user %s to group %s" % (request.user, group_request.user, group_request.group.name))
            group_request.delete()
    except:
        logger.exception("Unhandled exception occured while user %s attempting to reject group request id %s" % (request.user, group_request_id))
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_leave_accept_request(request, group_request_id):
    logger.debug("group_leave_accept_request called by user %s for group request id %s" % (request.user, group_request_id))
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)
        group, created = Group.objects.get_or_create(name=group_request.group.name)
        group_request.user.groups.remove(group)
        group_request.user.save()
        group_request.delete()
        logger.info("User %s accepted group leave request from user %s to group %s" % (request.user, group_request.user, group_request.group.name))
    except:
        logger.exception("Unhandled exception occured while user %s attempting to accept group leave request id %s" % (request.user, group_request_id))
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_leave_reject_request(request, group_request_id):
    logger.debug("group_leave_reject_request called by user %s for group request id %s" % (request.user, group_request_id))
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)

        if group_request:
            group_request.delete()
            logger.info("User %s rejected group leave request from user %s for group %s" % (request.user, group_request.user, group_request.group.name))
    except:
        logger.exception("Unhandled exception occured while user %s attempting to reject group leave request id %s" % (request.user, group_request_id))
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
def groups_view(request):
    logger.debug("groups_view called by user %s" % request.user)
    paired_list = []

    for group in Group.objects.all():
        # Check if group is a corp
        if "Corp_" in group.name:
            pass
        elif settings.DEFAULT_AUTH_GROUP in group.name:
            pass
        elif settings.DEFAULT_BLUE_GROUP in group.name:
            pass
        elif HiddenGroup.objects.filter(group=group).exists():
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
    logger.debug("group_request_add called by user %s for group id %s" % (request.user, group_id))
    group = Group.objects.get(id=group_id)
    if OpenGroup.objects.filter(group=group).exists():
        logger.info("%s joining %s as is an open group" % (request.user, group))
        request.user.groups.add(group)
        return HttpResponseRedirect("/groups")
    auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
    grouprequest = GroupRequest()
    grouprequest.status = 'pending'
    grouprequest.group = group
    grouprequest.user = request.user
    grouprequest.main_char = EveManager.get_character_by_id(auth_info.main_char_id)
    grouprequest.leave_request = False
    grouprequest.save()
    logger.info("Created group request for user %s to group %s" % (request.user, Group.objects.get(id=group_id)))

    return HttpResponseRedirect("/groups")


@login_required
def group_request_leave(request, group_id):
    logger.debug("group_request_leave called by user %s for group id %s" % (request.user, group_id))
    group = Group.objects.get(id=group_id)
    if OpenGroup.objects.filter(group=group).exists():
        logger.info("%s leaving %s as is an open group" % (request.user, group))
        request.user.groups.remove(group)
        return HttpResponseRedirect("/groups")
    auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
    grouprequest = GroupRequest()
    grouprequest.status = 'pending'
    grouprequest.group = group
    grouprequest.user = request.user
    grouprequest.main_char = EveManager.get_character_by_id(auth_info.main_char_id)
    grouprequest.leave_request = True
    grouprequest.save()
    logger.info("Created group leave request for user %s to group %s" % (request.user, Group.objects.get(id=group_id)))

    return HttpResponseRedirect("/groups")
