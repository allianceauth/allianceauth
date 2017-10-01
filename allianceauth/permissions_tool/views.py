import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, User
from django.db.models import Count
from django.shortcuts import render, Http404


logger = logging.getLogger(__name__)


@login_required
@permission_required('permissions_tool.audit_permissions')
def permissions_overview(request):
    logger.debug("permissions_overview called by user %s" % request.user)
    perms = Permission.objects.select_related('content_type').all()\
        .annotate(Count('user', distinct=True))\
        .annotate(Count('group', distinct=True)) \
        .annotate(Count('group__user', distinct=True)) \
        .annotate(Count('state', distinct=True))\
        .annotate(Count('state__userprofile', distinct=True))

    get_all = True if request.GET.get('all', 'no') == 'yes' else False

    context = {'permissions': []}
    for perm in perms:
        this_perm = {
            'users': perm.user__count,
            'groups': perm.group__count,
            'group_users': perm.group__user__count,
            'states': perm.state__count,
            'state_users': perm.state__userprofile__count,
            'permission': perm,
        }

        if get_all or sum([this_perm['users'], this_perm['groups'], this_perm['states']]) > 0:
            # Only add if we're getting everything or one of the objects has this permission
            context['permissions'].append(this_perm)

    return render(request, 'permissions_tool/overview.html', context=context)


@login_required
@permission_required('permissions_tool.audit_permissions')
def permissions_audit(request, app_label, model, codename):
    logger.debug("permissions_audit called by user {} on {}:{}:{}".format(request.user, app_label, model, codename))
    try:
        perm = Permission.objects\
            .prefetch_related('group_set', 'user_set', 'state_set',
                              'state_set__userprofile_set', 'group_set__user_set', 'state_set__userprofile_set__user')\
            .get(content_type__app_label=app_label, content_type__model=model, codename=codename)
    except Permission.DoesNotExist:
        raise Http404

    context = {'permission': {
        'permission': perm,
        'users': perm.user_set.all(),
        'groups': perm.group_set.all(),
        'states': perm.state_set.all(),
        'group_users': [group.user_set.all() for group in perm.group_set.all()],
        'state_users': [state.userprofile_set.all() for state in perm.state_set.all()],
        }
    }

    return render(request, 'permissions_tool/audit.html', context=context)
