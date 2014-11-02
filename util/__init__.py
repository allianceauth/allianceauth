from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


def bootstrap_permissions():
    ct = ContentType.objects.get_for_model(User)
    Permission.objects.get_or_create(codename="group_management", content_type=ct, name="group_management")
    Permission.objects.get_or_create(codename="jabber_broadcast", content_type=ct, name="jabber_broadcast")
    Permission.objects.get_or_create(codename="human_resources", content_type=ct, name="human_resources")


def add_member_permission(user, permission):
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)

    if User.objects.filter(username=user.username).exists():
        user = User.objects.get(username=user.username)
        user.user_permissions.add(stored_permission)
        user.save()


def remove_member_permission(user, permission):
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)
    if User.objects.filter(username=user.username).exists():
        user = User.objects.get(username=user.username)
        if user.has_perm(permission):
            user.user_permissions.remove(stored_permission)
            user.save()


def check_if_user_has_permission(user, permission):
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)
    return user.has_perm(stored_permission)