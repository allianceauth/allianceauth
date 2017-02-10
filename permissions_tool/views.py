from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

import logging

logger = logging.getLogger(__name__)


@login_required
@permission_required('permissions_tool.audit_permissions')
def permissions_overview(request):
    logger.debug("permissions_overview called by user %s" % request.user)
    perms = Permission.objects.all()

    get_all = True if request.GET.get('all', 'no') == 'yes' else False

    context = {'permissions': []}
    for perm in perms:
        this_perm = {
            'users': perm.user_set.all().count(),
            'groups': perm.group_set.all().count(),
            'permission': perm
        }

        if get_all or this_perm['users'] > 0 or this_perm['groups'] > 0:
            # Only add if we're getting everything or one of the objects has this permission
            # Add group_users separately to improve performance
            this_perm['group_users'] = sum(group.user_count for group in
                                           perm.group_set.annotate(user_count=Count('user')))
            context['permissions'].append(this_perm)

    return render(request, 'permissions_tool/overview.html', context=context)


@login_required
@permission_required('permissions_tool.audit_permissions')
def permissions_audit(request, app_label, model, codename):
    logger.debug("permissions_audit called by user {} on {}:{}:{}".format(request.user, app_label, model, codename))
    perm = get_object_or_404(Permission,
                             content_type__app_label=app_label,
                             content_type__model=model,
                             codename=codename)

    context = {'permission': {
        'permission': perm,
        'users': perm.user_set.all(),
        'groups': perm.group_set.all(),
        'group_users': [group.user_set.all() for group in perm.group_set.all()]
        }
    }

    return render(request, 'permissions_tool/audit.html', context=context)
