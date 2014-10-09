from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


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