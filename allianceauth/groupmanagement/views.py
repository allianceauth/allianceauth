import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from .managers import GroupManager
from .models import GroupRequest

from allianceauth.notifications import notify

logger = logging.getLogger(__name__)


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_management(request):
    logger.debug("group_management called by user %s" % request.user)
    acceptrequests = []
    leaverequests = []

    base_group_query = GroupRequest.objects.select_related('user', 'group')
    if GroupManager.has_management_permission(request.user):
        # Full access
        group_requests = base_group_query.all()
    else:
        # Group specific leader
        group_requests = base_group_query.filter(group__authgroup__group_leaders__in=[request.user])

    for grouprequest in group_requests:
        if grouprequest.leave_request:
            leaverequests.append(grouprequest)
        else:
            acceptrequests.append(grouprequest)

    logger.debug("Providing user %s with %s acceptrequests and %s leaverequests." % (
        request.user, len(acceptrequests), len(leaverequests)))

    render_items = {'acceptrequests': acceptrequests, 'leaverequests': leaverequests}

    return render(request, 'groupmanagement/index.html', context=render_items)


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_membership(request):
    logger.debug("group_membership called by user %s" % request.user)
    # Get all open and closed groups
    if GroupManager.has_management_permission(request.user):
        # Full access
        groups = GroupManager.get_joinable_groups()
    else:
        # Group leader specific
        groups = GroupManager.get_group_leaders_groups(request.user)

    groups = groups.exclude(authgroup__internal=True).annotate(num_members=Count('user')).order_by('name')

    render_items = {'groups': groups}

    return render(request, 'groupmanagement/groupmembership.html', context=render_items)


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_membership_list(request, group_id):
    logger.debug("group_membership_list called by user %s for group id %s" % (request.user, group_id))
    group = get_object_or_404(Group, id=group_id)
    try:

        # Check its a joinable group i.e. not corp or internal
        # And the user has permission to manage it
        if not GroupManager.joinable_group(group) or not GroupManager.can_manage_group(request.user, group):
            logger.warning("User %s attempted to view the membership of group %s but permission was denied" %
                           (request.user, group_id))
            raise PermissionDenied

    except ObjectDoesNotExist:
        raise Http404("Group does not exist")

    members = list()

    for member in group.user_set.select_related('profile').all().order_by('username'):

        members.append({
            'user': member,
            'main_char': member.profile.main_character
        })

    render_items = {'group': group, 'members': members}

    return render(request, 'groupmanagement/groupmembers.html', context=render_items)


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_membership_remove(request, group_id, user_id):
    logger.debug("group_membership_remove called by user %s for group id %s on user id %s" %
                 (request.user, group_id, user_id))
    group = get_object_or_404(Group, id=group_id)
    try:
        # Check its a joinable group i.e. not corp or internal
        # And the user has permission to manage it
        if not GroupManager.joinable_group(group) or not GroupManager.can_manage_group(request.user, group):
            logger.warning("User %s attempted to remove a user from group %s but permission was denied" % (request.user,
                                                                                                           group_id))
            raise PermissionDenied

        try:
            user = group.user_set.get(id=user_id)
            # Remove group from user
            user.groups.remove(group)
            logger.info("User %s removed user %s from group %s" % (request.user, user, group))
            messages.success(request, _("Removed user %(user)s from group %(group)s.") % {"user": user, "group": group})
        except ObjectDoesNotExist:
            messages.warning(request, _("User does not exist in that group"))

    except ObjectDoesNotExist:
        messages.warning(request, _("Group does not exist"))

    return redirect('groupmanagement:membership_list', group_id)


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_accept_request(request, group_request_id):
    logger.debug("group_accept_request called by user %s for grouprequest id %s" % (request.user, group_request_id))
    group_request = get_object_or_404(GroupRequest, id=group_request_id)
    try:
        group, created = Group.objects.get_or_create(name=group_request.group.name)

        if not GroupManager.joinable_group(group_request.group) or \
                not GroupManager.can_manage_group(request.user, group_request.group):
            raise PermissionDenied

        group_request.user.groups.add(group)
        group_request.user.save()
        group_request.delete()
        logger.info("User %s accepted group request from user %s to group %s" % (
            request.user, group_request.user, group_request.group.name))
        notify(group_request.user, "Group Application Accepted", level="success",
               message="Your application to %s has been accepted." % group_request.group)
        messages.success(request,
                         _('Accepted application from %(mainchar)s to %(group)s.') % {"mainchar": group_request.main_char, "group": group_request.group})

    except PermissionDenied as p:
        logger.warning("User %s attempted to accept group join request %s but permission was denied" %
                       (request.user, group_request_id))
        raise p
    except:
        messages.error(request, _('An unhandled error occurred while processing the application from %(mainchar)s to %(group)s.') % {"mainchar": group_request.main_char, "group": group_request.group})
        logger.exception("Unhandled exception occurred while user %s attempting to accept grouprequest id %s." % (
            request.user, group_request_id))
        pass

    return redirect("groupmanagement:management")


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_reject_request(request, group_request_id):
    logger.debug("group_reject_request called by user %s for group request id %s" % (request.user, group_request_id))
    group_request = get_object_or_404(GroupRequest, id=group_request_id)
    try:
        if not GroupManager.can_manage_group(request.user, group_request.group):
            raise PermissionDenied

        if group_request:
            logger.info("User %s rejected group request from user %s to group %s" % (
                request.user, group_request.user, group_request.group.name))
            group_request.delete()
            notify(group_request.user, "Group Application Rejected", level="danger",
                   message="Your application to %s has been rejected." % group_request.group)
            messages.success(request,
                             _('Rejected application from %(mainchar)s to %(group)s.') % {"mainchar": group_request.main_char, "group": group_request.group})

    except PermissionDenied as p:
        logger.warning("User %s attempted to reject group join request %s but permission was denied" %
                       (request.user, group_request_id))
        raise p
    except:
        messages.error(request, _('An unhandled error occurred while processing the application from %(mainchar)s to %(group)s.') % {"mainchar": group_request.main_char, "group": group_request.group})
        logger.exception("Unhandled exception occured while user %s attempting to reject group request id %s" % (
            request.user, group_request_id))
        pass

    return redirect("groupmanagement:management")


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_leave_accept_request(request, group_request_id):
    logger.debug(
        "group_leave_accept_request called by user %s for group request id %s" % (request.user, group_request_id))
    group_request = get_object_or_404(GroupRequest, id=group_request_id)
    try:
        if not GroupManager.can_manage_group(request.user, group_request.group):
            raise PermissionDenied

        group, created = Group.objects.get_or_create(name=group_request.group.name)
        group_request.user.groups.remove(group)
        group_request.user.save()
        group_request.delete()
        logger.info("User %s accepted group leave request from user %s to group %s" % (
            request.user, group_request.user, group_request.group.name))
        notify(group_request.user, "Group Leave Request Accepted", level="success",
               message="Your request to leave %s has been accepted." % group_request.group)
        messages.success(request,
                         _('Accepted application from %(mainchar)s to leave %(group)s.') % {"mainchar": group_request.main_char, "group": group_request.group})
    except PermissionDenied as p:
        logger.warning("User %s attempted to accept group leave request %s but permission was denied" %
                       (request.user, group_request_id))
        raise p
    except:
        messages.error(request, _('An unhandled error occured while processing the application from %(mainchar)s to leave %(group)s.') % {
            "mainchar": group_request.main_char, "group": group_request.group})
        logger.exception("Unhandled exception occured while user %s attempting to accept group leave request id %s" % (
            request.user, group_request_id))
        pass

    return redirect("groupmanagement:management")


@login_required
@user_passes_test(GroupManager.can_manage_groups)
def group_leave_reject_request(request, group_request_id):
    logger.debug(
        "group_leave_reject_request called by user %s for group request id %s" % (request.user, group_request_id))
    group_request = get_object_or_404(GroupRequest, id=group_request_id)
    try:
        if not GroupManager.can_manage_group(request.user, group_request.group):
            raise PermissionDenied

        if group_request:
            group_request.delete()
            logger.info("User %s rejected group leave request from user %s for group %s" % (
                request.user, group_request.user, group_request.group.name))
            notify(group_request.user, "Group Leave Request Rejected", level="danger",
                   message="Your request to leave %s has been rejected." % group_request.group)
            messages.success(request, _('Rejected application from %(mainchar)s to leave %(group)s.') % {
                "mainchar": group_request.main_char, "group": group_request.group})
    except PermissionDenied as p:
        logger.warning("User %s attempted to reject group leave request %s but permission was denied" %
                       (request.user, group_request_id))
        raise p
    except:
        messages.error(request, _('An unhandled error occured while processing the application from %(mainchar)s to leave %(group)s.') % {
            "mainchar": group_request.main_char, "group": group_request.group})
        logger.exception("Unhandled exception occured while user %s attempting to reject group leave request id %s" % (
            request.user, group_request_id))
        pass

    return redirect("groupmanagement:management")


@login_required
def groups_view(request):
    logger.debug("groups_view called by user %s" % request.user)
    groups = []

    group_query = GroupManager.get_joinable_groups()

    if not request.user.has_perm('groupmanagement.request_groups'):
        # Filter down to public groups only for non-members
        group_query = group_query.filter(authgroup__public=True)
        logger.debug("Not a member, only public groups will be available")

    for group in group_query:
        # Exclude hidden
        if not group.authgroup.hidden:
            group_request = GroupRequest.objects.filter(user=request.user).filter(group=group)

            groups.append({'group': group, 'request': group_request[0] if group_request else None})

    render_items = {'groups': groups}
    return render(request, 'groupmanagement/groups.html', context=render_items)


@login_required
def group_request_add(request, group_id):
    logger.debug("group_request_add called by user %s for group id %s" % (request.user, group_id))
    group = Group.objects.get(id=group_id)
    if not GroupManager.joinable_group(group):
        logger.warning("User %s attempted to join group id %s but it is not a joinable group" %
                       (request.user, group_id))
        messages.warning(request, _("You cannot join that group"))
        return redirect('groupmanagement:groups')
    if not request.user.has_perm('groupmanagement.request_groups') and not group.authgroup.public:
        # Does not have the required permission, trying to join a non-public group
        logger.warning("User %s attempted to join group id %s but it is not a public group" %
                       (request.user, group_id))
        messages.warning(request, "You cannot join that group")
        return redirect('groupmanagement:groups')
    if group.authgroup.open:
        logger.info("%s joining %s as is an open group" % (request.user, group))
        request.user.groups.add(group)
        return redirect("groupmanagement:groups")
    grouprequest = GroupRequest()
    grouprequest.status = _('Pending')
    grouprequest.group = group
    grouprequest.user = request.user
    grouprequest.leave_request = False
    grouprequest.save()
    logger.info("Created group request for user %s to group %s" % (request.user, Group.objects.get(id=group_id)))
    messages.success(request, _('Applied to group %(group)s.') % {"group": group})
    return redirect("groupmanagement:groups")


@login_required
def group_request_leave(request, group_id):
    logger.debug("group_request_leave called by user %s for group id %s" % (request.user, group_id))
    group = Group.objects.get(id=group_id)
    if not GroupManager.joinable_group(group):
        logger.warning("User %s attempted to leave group id %s but it is not a joinable group" %
                       (request.user, group_id))
        messages.warning(request, _("You cannot leave that group"))
        return redirect('groupmanagement:groups')
    if group not in request.user.groups.all():
        logger.debug("User %s attempted to leave group id %s but they are not a member" %
                     (request.user, group_id))
        messages.warning(request, _("You are not a member of that group"))
        return redirect('groupmanagement:groups')
    if group.authgroup.open:
        logger.info("%s leaving %s as is an open group" % (request.user, group))
        request.user.groups.remove(group)
        return redirect("groupmanagement:groups")
    grouprequest = GroupRequest()
    grouprequest.status = _('Pending')
    grouprequest.group = group
    grouprequest.user = request.user
    grouprequest.leave_request = True
    grouprequest.save()
    logger.info("Created group leave request for user %s to group %s" % (request.user, Group.objects.get(id=group_id)))
    messages.success(request, _('Applied to leave group %(group)s.') % {"group": group})
    return redirect("groupmanagement:groups")
