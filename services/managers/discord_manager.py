import requests
import json
from django.conf import settings
import re
import os
from services.models import DiscordAuthToken

import logging

logger = logging.getLogger(__name__)

DISCORD_URL = "https://discordapp.com/api"

class DiscordAPIManager:

    def __init__(self, server_id, email, password):
#        data = {
#            "email" : email,
#            "password": password,
#        }
#        custom_headers = {'content-type':'application/json'}
#        path = DISCORD_URL + "/auth/login"
#        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
#        r.raise_for_status()
        self.token = DiscordAPIManager.get_token_by_user(email, password)
        self.email = email
        self.password = password
        self.server_id = server_id
        logger.debug("Initialized DiscordAPIManager with server id %s" % self.server_id)

    def __del__(self):
        if hasattr(self, 'token'):
            if self.token and self.token != "":
                data = {'token': self.token}
                path = DISCORD_URL + "/auth/logout"
                custom_headers = {'content-type':'application/json'}
                r = requests.post(path, headers=custom_headers, data=json.dumps(data))
                r.raise_for_status()

    @staticmethod
    def validate_token(token):
        custom_headers = {'accept': 'application/json', 'authorization': token}
        path = DISCORD_URL + "/users/@me"
        r = requests.get(path, headers=custom_headers)
        if r.status_code == 200:
            logger.debug("Token starting with %s still valid." % token[0:5])
            return True
        else:
            logger.debug("Token starting with %s vailed validation with status code %s" % (token[0:5], r.status_code))
            return False        

    @staticmethod
    def get_auth_token():
        data = {
            "email" : settings.DISCORD_USER_EMAIL,
            "password": settings.DISCORD_USER_PASSWORD,
        }
        custom_headers = {'content-type':'application/json'}
        path = DISCORD_URL + "/auth/login"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        logger.debug("Received status code %s during token generation for settings discord user." % r.status_code)
        r.raise_for_status()
        return r.json()['token']

    def add_server(self, name):
        data = {"name": name}
        custom_headers = {'content-type':'application/json', 'authorization': self.token}
        path = DISCORD_URL + "/guilds"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    def rename_server(self, name):
        data = {"name": name}
        custom_headers = {'content-type':'application/json', 'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id)
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    def delete_server(self):
        custom_headers = {'content-type':'application/json', 'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    def get_members(self):
        custom_headers = {'accept':'application/json', 'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/members"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    def get_bans(self):
        custom_headers = {'accept':'application/json', 'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/bans"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    def ban_user(self, user_id, delete_message_age=0):
        custom_headers = {'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/bans/" + str(user_id) + "?delete-message-days=" + str(delete_message_age)
        r = requests.put(path, headers=custom_headers)
        r.raise_for_status()

    def unban_user(self, user_id):
        custom_headers = {'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/bans/" + str(user_id)
        r = requests.delete(path, headers=custom_headers)
        logger.debug("Received status code %s after deleting ban for user %s" % (r.status_code, user_id))
        r.raise_for_status()

    def generate_role(self):
        custom_headers = {'accept':'application/json', 'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/roles"
        r = requests.post(path, headers=custom_headers)
        logger.debug("Received status code %s after generating new role." % r.status_code)
        r.raise_for_status()
        return r.json()

    def edit_role(self, role_id, name, color=0, hoist=True, permissions=36785152):
        custom_headers = {'content-type':'application/json', 'authorization': self.token}
        data = {
            'color': color,
            'hoist': hoist,
            'name':  name,
            'permissions': permissions,
        }
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/roles/" + str(role_id)
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        logger.debug("Received status code %s after editing role id %s" % (r.status_code, role_id))
        r.raise_for_status()
        return r.json()

    def delete_role(self, role_id):
        custom_headers = {'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/roles/" + str(role_id)
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
    def accept_invite(invite_id, token):
        custom_headers = {'accept': 'application/json', 'authorization': token}
        path = DISCORD_URL + "/invite/" + str(invite_id)
        r = requests.post(path, headers=custom_headers)
        logger.debug("Received status code %s after accepting invite." % r.status_code)
        r.raise_for_status()
        return r.json()

    def create_invite(self, max_age=600, max_uses=1, temporary=True, xkcdpass=False):
        custom_headers = {'authorization': self.token}
        path = DISCORD_URL + "/channels/" + str(self.server_id) + "/invites"
        data = {
            'max_age': max_age,
            'max_uses': max_uses,
            'temporary': temporary,
            'xkcdpass': xkcdpass,
        }
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        logger.debug("Received status code %s after creating invite." % r.status_code)
        r.raise_for_status()
        return r.json()

    def delete_invite(self, invite_id):
        custom_headers = {'authorization': self.token}
        path = DISCORD_URL + "/invite/" + str(invite_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    def set_roles(self, user_id, role_ids):
        custom_headers = {'authorization': self.token, 'content-type':'application/json'}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/members/" + str(user_id)
        data = { 'roles': role_ids }
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        logger.debug("Received status code %s after setting roles of user %s to %s" % (r.status_code, user_id, role_ids))
        r.raise_for_status()

    @staticmethod
    def register_user(server_id, username, invite_code, password, email):
        custom_headers = {'content-type': 'application/json'}
        data = {
            'fingerprint': None,
            'username': username,
            'invite': invite_code,
            'password': password,
            'email': email,
        }
        path = DISCORD_URL + "/auth/register"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()

    def kick_user(self, user_id):
        custom_headers = {'authorization': self.token}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/members/" + str(user_id)
        r = requests.delete(path, headers=custom_headers)
        r.raise_for_status()

    def get_members(self):
        custom_headers = {'authorization': self.token, 'accept':'application/json'}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/members"
        r = requests.get(path, headers=custom_headers)
        r.raise_for_status()
        return r.json()

    def get_user_id(self, username):
        all_members = self.get_members()
        for member in all_members:
            if member['user']['username'] == username:
                return member['user']['id']
        raise KeyError('User not found on server: ' + username)

    def get_roles(self):
        custom_headers = {'authorization': self.token, 'accept':'application/json'}
        path = DISCORD_URL + "/guilds/" + str(self.server_id) + "/roles"
        r = requests.get(path, headers=custom_headers)
        logger.debug("Received status code %s after retrieving role list from server." % r.status_code)
        r.raise_for_status()
        return r.json()

    def get_group_id(self, group_name):
        logger.debug("Determining role id for group name %s" % group_name)
        all_roles = self.get_roles()
        logger.debug("Retrieved role list for server: %s" % all_roles)
        for role in all_roles:
            logger.debug("Checking role %s" % role)
            if role['name'] == group_name:
                logger.debug("Found role matching name: %s" % role['id'])
                return role['id']
        logger.debug("Role not found on server. Raising KeyError")
        raise KeyError('Group not found on server: ' + group_name)

    @staticmethod
    def get_token_by_user(email, password):
        if DiscordAuthToken.objects.filter(email=email).exists():
            logger.debug("Discord auth token cached for supplied email starting with %s" % email[0:3])
            auth = DiscordAuthToken.objects.get(email=email)
            if DiscordAPIManager.validate_token(auth.token):
                logger.debug("Token still valid. Returning token starting with %s" % auth.token[0:5])
                return auth.token
            else:
                logger.debug("Token has expired. Deleting.")
                auth.delete()
        logger.debug("Generating auth token for email starting with %s and password of length %s" % (email[0:3], len(password)))
        data = {
            "email" : email,
            "password": password,
        }
        custom_headers = {'content-type':'application/json'}
        path = DISCORD_URL + "/auth/login"
        r = requests.post(path, headers=custom_headers, data=json.dumps(data))
        logger.debug("Received status code %s after generating auth token for custom user." % r.status_code)
        r.raise_for_status()
        token = r.json()['token']
        auth = DiscordAuthToken(email=email, token=token)
        auth.save()
        logger.debug("Created cached token for email starting with %s" % email[0:3])
        return token

    @staticmethod
    def get_user_profile(email, password):
        token = DiscordAPIManager.get_token_by_user(email, password)
        custom_headers = {'accept': 'application/json', 'authorization': token}
        path = DISCORD_URL + "/users/@me"
        r = requests.get(path, headers=custom_headers)
        logger.debug("Received status code %s after retrieving user profile with email %s" % (r.status_code, email[0:3]))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def set_user_password(email, current_password, new_password):
        profile = DiscordAPIManager.get_user_profile(email, current_password)
        avatar = profile['avatar']
        username = profile['username']
        data = {
            'avatar': avatar,
            'username': username,
            'password': current_password,
            'new_password': new_password,
            'email': email,
        }
        path = DISCORD_URL + "/users/@me"
        custom_headers = {'content-type':'application/json', 'authorization': DiscordAPIManager.get_token_by_user(email, current_password)}
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def destroy_user(email, current_password):
        data = {
            'avatar': None,
            'username': os.urandom(8).encode('hex'),
            'password': current_password,
            'email': os.urandom(8).encode('hex') + '@test.com',
        }
        path = DISCORD_URL + "/users/@me"
        custom_headers = {'content-type':'application/json', 'authorization': DiscordAPIManager.get_token_by_user(email, current_password)}
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        r.raise_for_status
        return r.json()

    def check_if_user_banned(self, user_id):
        bans = self.get_bans()
        for b in bans:
            if b['user']['id'] == str(user_id):
                return True
        return False

class DiscordManager:
    def __init__(self):
        pass

    @staticmethod
    def __sanatize_username(username):
        clean = re.sub(r'[^\w]','_', username)
        return clean

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def update_groups(user_id, groups):
        logger.debug("Updating groups for user_id %s: %s" % (user_id, groups))
        group_ids = []
        api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
        if len(groups) == 0:
            logger.debug("No groups provided - generating empty array of group ids.")
            group_ids = []
        else:
            for g in groups:
                try:
                    logger.debug("Retrieving group id for group %s" % g)
                    group_id = api.get_group_id(g)
                    group_ids.append(group_id)
                    logger.debug("Got id %s" % group_id)
                except:
                    logger.debug("Group id retrieval generated exception - generating new group on discord server.", exc_info=True)
                    group_ids.append(DiscordManager.create_group(g))
        logger.debug("Setting groups for user %s to %s" % (user_id, group_ids))
        api.set_roles(user_id, group_ids)

    @staticmethod
    def create_group(groupname):
        logger.debug("Creating new group %s" % groupname)
        api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
        new_group = api.generate_role()
        logger.debug("Created new role on server with id %s: %s" % (new_group['id'], new_group))
        named_group = api.edit_role(new_group['id'], groupname)
        logger.debug("Renamed group id %s to %s" % (new_group['id'], groupname))
        return named_group['id']

    @staticmethod
    def lock_user(user_id):
        try:
            api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
            api.ban_user(user_id)
            return True
        except:
            return False

    @staticmethod
    def unlock_user(user_id):
        try:
            api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
            api.unban_user(user_id)
            return True
        except:
            return False

    @staticmethod
    def update_user_password(email, current_password):
        new_password = DiscordManager.__generate_random_pass()
        try:
            profile = DiscordAPIManager.set_user_password(email, current_password, new_password)
            return new_password
        except:
            return current_password

    @staticmethod
    def add_user(email, password):
        try:
            logger.debug("Adding new user to discord with email %s and password of length %s" % (email[0:3], len(password)))
            api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
            profile = DiscordAPIManager.get_user_profile(email, password)
            logger.debug("Got profile for user: %s" % profile)
            user_id = profile['id']
            logger.debug("Determined user id: %s" % user_id)
            if api.check_if_user_banned(user_id):
                logger.debug("User is currently banned. Unbanning %s" % user_id)
                api.unban_user(user_id)
            invite_code = api.create_invite()['code']
            logger.debug("Generated invite code beginning with %s" % invite_code[0:5])
            token = DiscordAPIManager.get_token_by_user(email, password)
            logger.debug("Got auth token for supplied credentials beginning with %s" % token[0:5])
            DiscordAPIManager.accept_invite(invite_code, token)
            logger.debug("Added user to server with id %s" % user_id)
            return user_id
        except:
            logger.exception("An unhandled exception has occured.", exc_info=True)
            return ""

    @staticmethod
    def delete_user(user_id):
        try:
            api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
            DiscordManager.update_groups(user_id, [])
            api.ban_user(user_id)
            return True
        except:
            return False
