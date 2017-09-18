from allianceauth.groupmanagement.managers import GroupManager


def can_manage_groups(request):
    return {'can_manage_groups': GroupManager.can_manage_groups(request.user)}
