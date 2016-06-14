import requests
import json
from django.conf import settings
import re
import os
import urllib
import base64
from services.models import DiscordAuthToken, GroupCache
from requests_oauthlib import OAuth2Session
import logging
import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

DISCORD_URL = "https://discordapp.com/api"
EVE_IMAGE_SERVER = "https://image.eveonline.com"

class DiscordAPIManager:

    def __init__(self, server_id, email, password, user=None):
        self.token = DiscordAPIManager.get_token_by_user(email, password, user)
        self.email = email
        self.password = password
        self.server_id = server_id
        logger.debug("Initialized DiscordAPIManager with server id %s" % self.server_id)

    @staticmethod
    def validate_token(token):
        custom_headers = {'accept': 'application/json', 'authorization': token}
        path = DISCORD_URL + "/users/@me"
        r = requests.get(path, headers=custom_headers)
        if r.status_code == 200:
            logger.debug("Token starting with %s passed validation." % token[0:5])
            return True
        else:
            logger.debug("Token starting with %s failed validation with status code %s" % (token[0:5], r.status_code))
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
        logger.debug("Received status code %s after banning user %s" % (r.status_code, user_id))
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

    def accept_invite(self, invite_id):
        custom_headers = {'accept': 'application/json', 'authorization': self.token}
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
    def get_token_by_user(email, password, user):
        if DiscordAuthToken.objects.filter(email=email).exists():
            auth = DiscordAuthToken.objects.get(email=email)
            if not auth.user == user:
                raise ValueError("User mismatch while validating DiscordAuthToken for email %s - user %s, requesting user %s" % (email, auth.user, user))                
            logger.debug("Discord auth token cached for supplied email starting with %s" % email[0:3])
            auth = DiscordAuthToken.objects.get(email=email, user=user)
            if DiscordAPIManager.validate_token(auth.token):
                logger.debug("Token still valid. Returning token starting with %s" % auth.token[0:5])
                return auth.token
            else:
                logger.debug("Token has expired. Deleting.")
                auth.delete()
        logger.debug("Generating auth token for email starting with %s user %s and password of length %s" % (email[0:3], user, len(password)))
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
        auth = DiscordAuthToken(email=email, token=token, user=user)
        auth.save()
        logger.debug("Created cached token for email starting with %s" % email[0:3])
        return token

    def get_profile(self):
        custom_headers = {'accept': 'application/json', 'authorization': self.token}
        path = DISCORD_URL + "/users/@me"
        r = requests.get(path, headers=custom_headers)
        logger.debug("Received status code %s after retrieving user profile with email %s" % (r.status_code, self.email[0:3]))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_user_profile(email, password, user):
        token = DiscordAPIManager.get_token_by_user(email, password, user)
        custom_headers = {'accept': 'application/json', 'authorization': token}
        path = DISCORD_URL + "/users/@me"
        r = requests.get(path, headers=custom_headers)
        logger.debug("Received status code %s after retrieving user profile with email %s" % (r.status_code, email[0:3]))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def set_user_password(email, current_password, new_password, user):
        profile = DiscordAPIManager.get_user_profile(email, current_password, user)
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
    def set_user_avatar(email, current_password, user, avatar_url):
        profile = DiscordAPIManager.get_user_profile(email, current_password, user)
        avatar = "data:image/jpeg;base64," + base64.b64encode(urllib.urlopen(avatar_url).read())
        username = profile['username']
        data = {
            'avatar': avatar,
            'username': username,
            'password': current_password,
            'email': email
        }
        path = DISCORD_URL + "/users/@me"
        custom_headers = {'content-type':'application/json', 'authorization': DiscordAPIManager.get_token_by_user(email, current_password, user)}
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
        logger.info("Setting discord groups for user %s to %s" % (user_id, group_ids))
        api.set_roles(user_id, group_ids)

    @staticmethod
    def create_group(groupname):
        logger.debug("Creating new group %s" % groupname)
        api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
        new_group = api.generate_role()
        logger.debug("Created new role on server with id %s: %s" % (new_group['id'], new_group))
        named_group = api.edit_role(new_group['id'], groupname)
        logger.debug("Renamed group id %s to %s" % (new_group['id'], groupname))
        logger.info("Created new group on discord server with name %s" % groupname)
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
    def update_user_password(email, current_password, user):
        new_password = DiscordManager.__generate_random_pass()
        try:
            profile = DiscordAPIManager.set_user_password(email, current_password, new_password, user)
            return new_password
        except:
            return current_password

    @staticmethod
    def update_user_avatar(email, password, user, char_id):
        try:
            char_url = EVE_IMAGE_SERVER + "/character/" + str(char_id) + "_256.jpg"
            logger.debug("Character image URL for %s: %s" % (user, char_url))
            DiscordAPIManager.set_user_avatar(email, password, user, char_url)
            return True
        except:
            return False

    @staticmethod
    def add_user(email, password, user):
        try:
            logger.debug("Adding new user %s to discord with email %s and password of length %s" % (user, email[0:3], len(password)))
            server_api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
            user_api = DiscordAPIManager(settings.DISCORD_SERVER_ID, email, password, user=user)
            profile = user_api.get_profile()
            logger.debug("Got profile for user: %s" % profile)
            user_id = profile['id']
            logger.debug("Determined user id: %s" % user_id)

            if server_api.check_if_user_banned(user_id):
                logger.debug("User is currently banned. Unbanning %s" % user_id)
                server_api.unban_user(user_id)
            invite_code = server_api.create_invite()['code']
            logger.debug("Generated invite code beginning with %s" % invite_code[0:5])
            user_api.accept_invite(invite_code)
            logger.info("Added user to discord server %s with id %s" % (settings.DISCORD_SERVER_ID, user_id))
            return user_id
        except:
            logger.exception("An unhandled exception has occured.")
            return ""

    @staticmethod
    def delete_user(user_id):
        try:
            logger.debug("Deleting user with id %s from discord server." % user_id)
            api = DiscordAPIManager(settings.DISCORD_SERVER_ID, settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
            DiscordManager.update_groups(user_id, [])
            api.ban_user(user_id)
            logger.info("Deleted user with id %s from discord server id %s" % (user_id, settings.DISCORD_SERVER_ID))
            return True
        except:
            logger.exception("An unhandled exception has occured.")
            return False

AUTH_URL = "https://discordapp.com/api/oauth2/authorize"
TOKEN_URL = "https://discordapp.com/api/oauth2/token"

# kick, manage roles
BOT_PERMISSIONS = 0x00000002 + 0x10000000

# get user ID, accept invite
SCOPES = [
    'identify',
    'guilds.join',
]

GROUP_CACHE_MAX_AGE = datetime.timedelta(minutes=30)

class DiscordOAuthManager:
    @staticmethod
    def generate_bot_add_url():
        return AUTH_URL + '?client_id=' + settings.DISCORD_APP_ID + '&scope=bot&permissions=' + str(BOT_PERMISSIONS)

    @staticmethod
    def generate_oauth_redirect_url():
        oauth = OAuth2Session(settings.DISCORD_APP_ID, redirect_uri=settings.DISCORD_CALLBACK_URL, scope=SCOPES)
        url, state = oauth.authorization_url(AUTH_URL)
        return url

    @staticmethod
    def _process_callback_code(code):
        oauth = OAuth2Session(settings.DISCORD_APP_ID, redirect_uri=settings.DISCORD_CALLBACK_URL)
        token = oauth.fetch_token(TOKEN_URL, client_secret=settings.DISCORD_APP_SECRET, code=code)
        return token

    @staticmethod
    def add_user(code):
        try:
            token = DiscordOAuthManager._process_callback_code(code)['access_token']
            logger.debug("Received token from OAuth")

            custom_headers = {'accept': 'application/json', 'authorization': 'Bearer ' + token}
            path = DISCORD_URL + "/invites/" + str(settings.DISCORD_INVITE_CODE)
            r = requests.post(path, headers=custom_headers)
            logger.debug("Got status code %s after accepting Discord invite" % r.status_code)
            r.raise_for_status()

            path = DISCORD_URL + "/users/@me"
            r = requests.get(path, headers=custom_headers)
            logger.debug("Got status code %s after retrieving Discord profile" % r.status_code)
            r.raise_for_status()

            user_id = r.json()['id']
            logger.info("Added Discord user ID %s to server." % user_id)
            return user_id
        except:
            logger.exception("Failed to add Discord user")
            return None

    @staticmethod
    def delete_user(user_id):
        try:
            custom_headers = {'accept': 'application/json', 'authorization': settings.DISCORD_BOT_TOKEN}
            path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/members/" + str(user_id)
            r = requests.delete(path, headers=custom_headers)
            logger.debug("Got status code %s after removing Discord user ID %s" % (r.status_code, user_id))
            r.raise_for_status()
            return True
        except:
            logger.exception("Failed to remove Discord user %s" % user_id)
            try:
                # user maybe already left server?
                custom_headers = {'accept': 'application/json', 'authorization': settings.DISCORD_BOT_TOKEN}
                path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/members"
                r = requests.get(path, headers=custom_headers)
                members = r.json()
                users = [str(m['user']['id']) == str(user_id) for m in members]
                if True in users:
                    logger.error("Unable to remove Discord user %s" % user_id)
                    return False
                else:
                    logger.warn("Discord user %s alredy left server." % user_id)
                    return True
            except:
                logger.exception("Failed to locate Discord user")
            return False

    @staticmethod
    def __get_groups():
        custom_headers = {'accept': 'application/json', 'authorization': settings.DISCORD_BOT_TOKEN}
        path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/roles"
        r = requests.get(path, headers=custom_headers)
        logger.debug("Got status code %s after retrieving Discord roles" % r.status_code)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def __update_group_cache():
        GroupCache.objects.filter(service="discord").delete()
        cache = GroupCache.objects.create(service="discord")
        cache.groups = json.dumps(DiscordOAuthManager.__get_groups())
        cache.save()
        return cache

    @staticmethod
    def __get_group_cache():
        if not GroupCache.objects.filter(service="discord").exists():
            DiscordOAuthManager.__update_group_cache()
        cache = GroupCache.objects.get(service="discord")
        age = timezone.now() - cache.created
        if age > GROUP_CACHE_MAX_AGE:
            logger.debug("Group cache has expired. Triggering update.")
            cache = DiscordOAuthManager.__update_group_cache()
        return json.loads(cache.groups)

    @staticmethod
    def __group_name_to_id(name):
        cache = DiscordOAuthManager.__get_group_cache()
        for g in cache:
            if g['name'] == name:
                return g['id']
        logger.debug("Group %s not found on Discord. Creating" % name)
        DiscordOAuthManager.__create_group(name)
        return DiscordOAuthManager.__group_name_to_id(name)

    @staticmethod
    def __group_id_to_name(id):
        cache = DiscordOAuthManager.__get_group_cache()
        for g in cache:
            if g['id'] == id:
                return g['name']
        raise KeyError("Group ID %s not found on Discord" % id)

    @staticmethod
    def __generate_role():
        custom_headers = {'accept':'application/json', 'authorization': settings.DISCORD_BOT_TOKEN}
        path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/roles"
        r = requests.post(path, headers=custom_headers)
        logger.debug("Received status code %s after generating new role." % r.status_code)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def __edit_role(role_id, name, color=0, hoist=True, permissions=36785152):
        custom_headers = {'content-type':'application/json', 'authorization': settings.DISCORD_BOT_TOKEN}
        data = {
            'color': color,
            'hoist': hoist,
            'name':  name,
            'permissions': permissions,
        }
        path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/roles/" + str(role_id)
        r = requests.patch(path, headers=custom_headers, data=json.dumps(data))
        logger.debug("Received status code %s after editing role id %s" % (r.status_code, role_id))
        r.raise_for_status()
        return r.json()

    @staticmethod
    def __create_group(name):
        role = DiscordOAuthManager.__generate_role()
        new_role = DiscordOAuthManager.__edit_role(role['id'], name)
        DiscordOAuthManager.__update_group_cache()

    @staticmethod
    def update_groups(user_id, groups):
        custom_headers = {'content-type':'application/json', 'authorization': settings.DISCORD_BOT_TOKEN}
        group_ids = [DiscordOAuthManager.__group_name_to_id(g) for g in groups]
        path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/members/" + str(user_id)
        data = {'roles': group_ids}
        r = requests.patch(path, headers=custom_headers, json=data)
        logger.debug("Received status code %s after setting user roles" % r.status_code)
        r.raise_for_status()
