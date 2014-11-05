from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from authentication.managers import AuthServicesInfoManager
from services.managers.jabber_manager import JabberManager
from services.managers.forum_manager import ForumManager
from services.managers.mumble_manager import MumbleManager


def add_user_to_group(user, groupname):
    user = User.objects.get(username=user.username)
    group, created = Group.objects.get_or_create(name=groupname)
    user.groups.add(group)
    user.save()


def remove_user_from_group(user, groupname):
    user = User.objects.get(username=user.username)
    group, created = Group.objects.get_or_create(name=groupname)
    if user.groups.filter(name=groupname):
        user.groups.remove(group)
        user.save()


def deactivate_services(user):
    authinfo = AuthServicesInfoManager.get_auth_service_info(user)
    if authinfo.mumble_username != "":
        MumbleManager.delete_user(authinfo.mumble_username)
        AuthServicesInfoManager.update_user_mumble_info("", "", user)
    if authinfo.jabber_username != "":
        JabberManager.delete_user(authinfo.jabber_username)
        AuthServicesInfoManager.update_user_jabber_info("", "", user)
    if authinfo.forum_username != "":
        ForumManager.disable_user(authinfo.forum_username)
        AuthServicesInfoManager.update_user_forum_info("", "", user)


def generate_corp_group_name(corpname):
    return 'Corp_' + corpname.replace(' ', '_')

