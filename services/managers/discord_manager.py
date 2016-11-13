from __future__ import unicode_literals
import requests
import json
import re
from django.conf import settings
from services.models import GroupCache
from requests_oauthlib import OAuth2Session
import logging
import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

DISCORD_URL = "https://discordapp.com/api"
EVE_IMAGE_SERVER = "https://image.eveonline.com"

AUTH_URL = "https://discordapp.com/api/oauth2/authorize"
TOKEN_URL = "https://discordapp.com/api/oauth2/token"

# needs administrator, since Discord can't get their permissions system to work
# was kick members, manage roles, manage nicknames
#BOT_PERMISSIONS = 0x00000002 + 0x10000000 + 0x08000000
BOT_PERMISSIONS = 0x00000008

# get user ID, accept invite
SCOPES = [
    'identify',
    'guilds.join',
]

GROUP_CACHE_MAX_AGE = datetime.timedelta(minutes=30)


class DiscordOAuthManager:
    def __init__(self):
        pass

    @staticmethod
    def _sanitize_groupname(name):
        name = name.strip(' _')
        return re.sub('[^\w.-]', '', name)

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
    def update_nickname(user_id, nickname):
        try:
            custom_headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
            data = {'nick': nickname, }
            path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/members/" + str(user_id)
            r = requests.patch(path, headers=custom_headers, json=data)
            logger.debug("Got status code %s after setting nickname for Discord user ID %s (%s)" % (
                r.status_code, user_id, nickname))
            if r.status_code == 404:
                logger.warn("Discord user ID %s could not be found in server." % user_id)
                return True
            r.raise_for_status()
            return True
        except:
            logger.exception("Failed to set nickname for Discord user ID %s (%s)" % (user_id, nickname))
            return False

    @staticmethod
    def delete_user(user_id):
        try:
            custom_headers = {'accept': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
            path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/members/" + str(user_id)
            r = requests.delete(path, headers=custom_headers)
            logger.debug("Got status code %s after removing Discord user ID %s" % (r.status_code, user_id))
            if r.status_code == 404:
                logger.warn("Discord user ID %s already left the server." % user_id)
                return True
            r.raise_for_status()
            return True
        except:
            logger.exception("Failed to remove Discord user ID %s" % user_id)
            return False

    @staticmethod
    def __get_groups():
        custom_headers = {'accept': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
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
        custom_headers = {'accept': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/roles"
        r = requests.post(path, headers=custom_headers)
        logger.debug("Received status code %s after generating new role." % r.status_code)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def __edit_role(role_id, name, color=0, hoist=True, permissions=36785152):
        custom_headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        data = {
            'color': color,
            'hoist': hoist,
            'name': name,
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
        DiscordOAuthManager.__edit_role(role['id'], name)
        DiscordOAuthManager.__update_group_cache()

    @staticmethod
    def update_groups(user_id, groups):
        custom_headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        group_ids = [DiscordOAuthManager.__group_name_to_id(DiscordOAuthManager._sanitize_groupname(g)) for g in groups]
        path = DISCORD_URL + "/guilds/" + str(settings.DISCORD_GUILD_ID) + "/members/" + str(user_id)
        data = {'roles': group_ids}
        r = requests.patch(path, headers=custom_headers, json=data)
        logger.debug("Received status code %s after setting user roles" % r.status_code)
        r.raise_for_status()
