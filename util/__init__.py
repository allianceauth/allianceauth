import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

def bootstrap_permissions():
    ct = ContentType.objects.get_for_model(User)
    Permission.objects.get_or_create(codename="member", content_type=ct, name="member")
    Permission.objects.get_or_create(codename="group_management", content_type=ct, name="group_management")
    Permission.objects.get_or_create(codename="jabber_broadcast", content_type=ct, name="jabber_broadcast")
    Permission.objects.get_or_create(codename="jabber_broadcast_all", content_type=ct, name="jabber_broadcast_all")
    Permission.objects.get_or_create(codename="human_resources", content_type=ct, name="human_resources")
    Permission.objects.get_or_create(codename="blue_member", content_type=ct, name="blue_member")
    Permission.objects.get_or_create(codename="corp_stats", content_type=ct, name="corp_stats")
    Permission.objects.get_or_create(codename="timer_management", content_type=ct, name="timer_management")
    Permission.objects.get_or_create(codename="timer_view", content_type=ct, name="timer_view")
    Permission.objects.get_or_create(codename="srp_management", content_type=ct, name="srp_management")
    Group.objects.get_or_create(name=settings.DEFAULT_AUTH_GROUP)
    Group.objects.get_or_create(name=settings.DEFAULT_BLUE_GROUP)
    logger.info("Bootstrapped permissions for auth and created default groups.")


def add_member_permission(user, permission):
    logger.debug("Adding permission %s to member %s" % (permission, user))
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)
    user = User.objects.get(username=user.username)
    user.user_permissions.add(stored_permission)
    logger.info("Added permission %s to user %s" % (permission, user))
    user.save()


def remove_member_permission(user, permission):
    logger.debug("Removing permission %s from member %s" % (permission, user))
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)

    user = User.objects.get(username=user.username)

    if user.has_perm('auth.' + permission):
        user.user_permissions.remove(stored_permission)
        user.save()
        logger.info("Removed permission %s from member %s" % (permission, user))
    else:
        logger.warn("Attempting to remove permission user %s does not have: %s" % (user, permission))


def check_if_user_has_permission(user, permission):
    ct = ContentType.objects.get_for_model(User)
    stored_permission, created = Permission.objects.get_or_create(codename=permission,
                                                                  content_type=ct, name=permission)
    return user.has_perm('auth.' + permission)


def random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.
