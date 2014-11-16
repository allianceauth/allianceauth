from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.conf import settings


def bootstrap_permissions():
    ct = ContentType.objects.get_for_model(User)
    Permission.objects.get_or_create(codename="alliance_member", content_type=ct, name="alliance_member")
    Permission.objects.get_or_create(codename="group_management", content_type=ct, name="group_management")
    Permission.objects.get_or_create(codename="jabber_broadcast", content_type=ct, name="jabber_broadcast")
    Permission.objects.get_or_create(codename="human_resources", content_type=ct, name="human_resources")
    Permission.objects.get_or_create(codename="blue_member", content_type=ct, name="blue_member")
    Permission.objects.get_or_create(codename="corp_stats", content_type=ct, name="corp_stats")
    Permission.objects.get_or_create(codename="timer_management", content_type=ct, name="timer_management")
    Group.objects.get_or_create(name=settings.DEFAULT_ALLIANCE_GROUP)
    Group.objects.get_or_create(name=settings.DEFAULT_BLUE_GROUP)


def add_member_permission(user, permission):
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)
    user = User.objects.get(username=user.username)
    user.user_permissions.add(stored_permission)
    user.save()


def remove_member_permission(user, permission):
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)

    user = User.objects.get(username=user.username)

    if user.has_perm('auth.' + permission):
        user.user_permissions.remove(stored_permission)
        user.save()


def check_if_user_has_permission(user, permission):
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)
    return user.has_perm('auth.' + permission)