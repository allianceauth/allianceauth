import requests
import json
from django.conf import settings
import re

DISCORD_URL = "https://discordapp.com/api"

class DiscordAPIManager:

    def __init__(self):
        pass

    @staticmethod
    def get_auth_token():
        data = {
            "email" : settings.DISCORD_USER_EMAIL,
            "password": settings.DISCORD_USER_PASSWORD,
        }
        custom_headers = {'content-type':'application/json'}
        path = DISCORD_URL + "/auth/login"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()['token']

    @staticmethod
    def add_server(name):
        data = {"name": name}
        custom_headers = {'content-type':'application/json', 'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def rename_server(server_id, name):
        data = {"name": name}
        custom_headers = {'content-type':'application/json', 'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id)
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def delete_server(server_id):
        custom_headers = {'content-type':'application/json', 'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def get_members(server_id):
        custom_headers = {'accept':'application/json', 'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/members"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_bans(server_id):
        custom_headers = {'accept':'application/json', 'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/bans"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def ban_user(server_id, user_id, delete_message_age=0):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/bans/" + str(user_id) + "?delete-message-days=" + str(delete_message_age)
        r = requests.put(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def unban_user(server_id, user_id):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/bans/" + str(user_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def generate_role(server_id):
        custom_headers = {'accept':'application/json', 'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/roles"
        r = requests.post(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def edit_role(server_id, role_id, name, color=0, hoist=True, permissions=36953089):
        custom_headers = {'content-type':'application/json', 'authorization': DiscordAPIManager.get_auth_token()}
        data = {
            'color': color,
            'hoist': hoist,
            'name':  name,
            'permissions': permissions,
        }
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/roles/" + str(role_id)
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    
    @staticmethod
    def delete_role(server_id, role_id):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/roles/" + str(role_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def get_invite(invite_id):
        custom_headers = {'accept': 'application/json'}
        path = DISCORD_URL + "/invite/" + str(invite_id)
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def accept_invite(invite_id):
        custom_headers = {'accept': 'application/json'}
        path = DISCORD_URL + "/invite/" + str(invite_id)
        r = requests.post(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_invite(server_id, max_age=0, max_users=1, temporary=True, xkcdpass=False):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/channels/" + str(server_id) + "/invites"
        data = {
            'max_age': max_age,
            'max_users': max_users,
            'temporary': temporary,
            'xkcdpass': xkcdpass,
        }
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def delete_invite(invite_id):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/invite/" + str(invite_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def set_roles(server_id, user_id, role_ids):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token(), 'content-type':'application/json'}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/members/" + str(user_id)
        data = { 'roles': role_ids }
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()

    @staticmethod
    def register_user(server_id, username, invite_code):
        custom_headers = {'content-type': 'application/json'}
        data = {
            'fingerprint': None,
            'username': username,
            'invite': invite_code,
        }
        path = DISCORD_URL + "/auth/register"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()

    @staticmethod
    def kick_user(server_id, user_id):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/members/" + str(user_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def get_members(server_id):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token(), 'accept':'application/json'}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/members"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_user_id(server_id, username):
        all_members = DiscordAPIManager.get_members(server_id)
        for member in all_members:
            if member['user']['username'] == username:
                return member['user']['id']
        raise KeyError('User not found on server: ' + username)

    @staticmethod
    def get_roles(server_id):
        custom_headers = {'authorization': DiscordAPIManager.get_auth_token(), 'accept':'application/json'}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/roles"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_group_id(server_id, group_name):
        all_roles = DiscordAPIManager.get_roles(server_id)
        for role in all_roles:
            if role['name'] == group_name:
                return role['id']
        raise KeyError('Group not found on server: ' + group_name)

class DiscordManager:
    def __init__(self):
        pass

    @staticmethod
    def __sanatize_username(username):
        clean = re.sub(r'[^\w]','_', username)
        return clean

    @staticmethod
    def add_user(username):
        try:
            username_clean = DiscordManager.__sanatize_username(username)
            invite_code = DiscordAPIManager.create_invite(settings.DISCORD_SERVER_ID)['code']
            DiscordAPIManager.register_user(settings.DISCORD_SERVER_ID, username_clean, invite_code)
            user_id = DiscordAPIManager.get_user_id(settings.DISCORD_SERVER_ID, username_clean)      
            return username_clean, user_id
        except:
            return "", ""

    @staticmethod
    def delete_user(username):
        try:
            user_id = DiscordAPIManager.get_user_id(username)
        except:
            #user does not exist
            return True
        try:
            DiscordAPIManager.kick_user(settings.DISCORD_SERVER_ID, user_id)
            return True
        except:
            return False

    @staticmethod
    def update_groups(username, groups):
        user_id = DiscordAPIManager.get_user_id(settings.DISCORD_SERVER_ID, username)
        group_ids = []
        for g in groups:
            try:
                group_id = DiscordAPIManager.get_group_id(settings.DISCORD_SERVER_ID, g)
                group_ids.append(group_id)
            except:
                # need to create role on server for group
                group_ids.append(DiscordManager.create_group(g))
        DiscordAPIManager.set_roles(settings.DISCORD_SERVER_ID, user_id, group_ids)

    @staticmethod
    def create_group(groupname):
        new_group = DiscordAPIManager.generate_role(settings.DISCORD_SERVER_ID)
        named_group = DiscordAPIManager.edit_role(settings.DISCORD_SERVER_ID, new_group['id'], groupname)
        return named_group['id']

    @staticmethod
    def lock_user(username):
        user_id = DiscordAPIManager.get_user_id(username)
        DiscordAPIManager.ban_user(settings.DISCORD_SERVER_ID, user_id)

    @staticmethod
    def unlock_user(username):
        user_id = DiscordAPIManager.get_user_id(username)
        DiscordAPIManager.unban_user(settings.DISCORD_SERVER_ID, user_id)
