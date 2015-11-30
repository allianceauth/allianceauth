import requests
import json
from django.conf import settings

DISCORD_URL = "https://discordapp.com/api"

class DiscordManager:

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
        custom_headers = {'content-type':'application/json', 'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def rename_server(server_id, name):
        data = {"name": name}
        custom_headers = {'content-type':'application/json', 'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id)
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def delete_server(server_id):
        custom_headers = {'content-type':'application/json', 'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def get_members(server_id):
        custom_headers = {'accept':'application/json', 'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/members"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_bans(server_id):
        custom_headers = {'accept':'application/json', 'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/bans"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def ban_user(server_id, user_id, delete_message_age=0):
        custom_headers = {'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/bans/" + str(user_id) + "?delete-message-days=" + str(delete_message_age)
        r = requests.put(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def unban_user(server_id, user_id):
        custom_headers = {'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/bans/" + str(user_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    @staticmethod
    def generate_role(server_id):
        custom_headers = {'accept':'application/json', 'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/roles"
        r = requests.post(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def edit_role(server_id, role_id, name, color=0, hoist=True, permissions=36953089):
        custom_headers = {'content-type':'application/json', 'authorization': DiscordManager.get_auth_token()}
        data = {
            'color': color,
            'hoist': hoist,
            'name': name,
            'permissions': permissions,
        }
        path = DISCORD_URL + "/guilds/" + str(server_id) + "/roles/" + str(role_id)
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    
    @staticmethod
    def delete_role(server_id, role_id):
        custom_headers = {'authorization': DiscordManager.get_auth_token()}
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
    def create_invite(channel_id):
        custom_headers = {'authorization': DiscordManager.get_auth_token()}
        path = DISCORD_URL + "/channels/" + str(channel_id) + "/invites"
        r = requests.post(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def delete_invite(invite_id):
        custom_headers = {'accept': 'application/json'}
        path = DISCORD_URL + "/invite/" + str(invite_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()
