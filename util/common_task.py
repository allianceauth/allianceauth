from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from authentication.managers import AuthServicesInfoManager
from services.managers.openfire_manager import OpenfireManager
from services.managers.phpbb3_manager import Phpbb3Manager
from services.managers.mumble_manager import MumbleManager
from services.managers.ipboard_manager import IPBoardManager
from services.managers.teamspeak3_manager import Teamspeak3Manager
from services.managers.discord_manager import DiscordManager


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
    if authinfo.mumble_username and authinfo.mumble_username != "":
        MumbleManager.delete_user(authinfo.mumble_username)
        AuthServicesInfoManager.update_user_mumble_info("", "", user)
    if authinfo.jabber_username and authinfo.jabber_username != "":
        OpenfireManager.delete_user(authinfo.jabber_username)
        AuthServicesInfoManager.update_user_jabber_info("", "", user)
    if authinfo.forum_username and authinfo.forum_username != "":
        Phpbb3Manager.disable_user(authinfo.forum_username)
        AuthServicesInfoManager.update_user_forum_info("", "", user)
    if authinfo.ipboard_username and authinfo.ipboard_username != "":
        IPBoardManager.disable_user(authinfo.ipboard_username)
        AuthServicesInfoManager.update_user_forum_info("", "", user)
    if authinfo.teamspeak3_uid and authinfo.teamspeak3_uid != "":
        Teamspeak3Manager.delete_user(authinfo.teamspeak3_uid)
        AuthServicesInfoManager.update_user_teamspeak3_info("", "", user)
    if authinfo.discord_username and authinfo.discord_username != "":
        DiscordManager.delete_user(authinfo.discord_username)
        AuthServicesInfoManager.update_user_discord_info("", "", user)


def generate_corp_group_name(corpname):
    return 'Corp_' + corpname.replace(' ', '_')

