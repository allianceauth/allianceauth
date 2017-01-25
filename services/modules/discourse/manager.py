from __future__ import unicode_literals
import logging
import requests
import random
import string
import datetime
import json
import re
from django.conf import settings
from django.utils import timezone
from services.models import GroupCache

logger = logging.getLogger(__name__)


class DiscourseError(Exception):
    def __init__(self, endpoint, errors):
        self.endpoint = endpoint
        self.errors = errors

    def __str__(self):
        return "API execution failed.\nErrors: %s\nEndpoint: %s" % (self.errors, self.endpoint)

# not exhaustive, only the ones we need
ENDPOINTS = {
    'groups': {
        'list': {
            'path': "/admin/groups.json",
            'method': requests.get,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'create': {
            'path': "/admin/groups",
            'method': requests.post,
            'args': {
                'required': ['name'],
                'optional': ['visible'],
            }
        },
        'add_user': {
            'path': "/admin/groups/%s/members.json",
            'method': requests.put,
            'args': {
                'required': ['usernames'],
                'optional': [],
            },
        },
        'remove_user': {
            'path': "/admin/groups/%s/members.json",
            'method': requests.delete,
            'args': {
                'required': ['username'],
                'optional': [],
            },
        },
        'delete': {
            'path': "/admin/groups/%s.json",
            'method': requests.delete,
            'args': {
                'required': [],
                'optional': [],
            },
        },
    },
    'users': {
        'create': {
            'path': "/users",
            'method': requests.post,
            'args': {
                'required': ['name', 'email', 'password', 'username'],
                'optional': ['active'],
            },
        },
        'update': {
            'path': "/users/%s.json",
            'method': requests.put,
            'args': {
                'required': ['params'],
                'optional': [],
            }
        },
        'get': {
            'path': "/users/%s.json",
            'method': requests.get,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'activate': {
            'path': "/admin/users/%s/activate",
            'method': requests.put,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'set_email': {
            'path': "/users/%s/preferences/email",
            'method': requests.put,
            'args': {
                'required': ['email'],
                'optional': [],
            },
        },
        'suspend': {
            'path': "/admin/users/%s/suspend",
            'method': requests.put,
            'args': {
                'required': ['duration', 'reason'],
                'optional': [],
            },
        },
        'unsuspend': {
            'path': "/admin/users/%s/unsuspend",
            'method': requests.put,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'logout': {
            'path': "/admin/users/%s/log_out",
            'method': requests.post,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'external': {
            'path': "/users/by-external/%s.json",
            'method': requests.get,
            'args': {
                'required': [],
                'optional': [],
            },
        },
    },
}


class DiscourseManager:
    def __init__(self):
        pass

    GROUP_CACHE_MAX_AGE = datetime.timedelta(minutes=30)
    REVOKED_EMAIL = 'revoked@' + settings.DOMAIN
    SUSPEND_DAYS = 99999
    SUSPEND_REASON = "Disabled by auth."

    @staticmethod
    def __exc(endpoint, *args, **kwargs):
        params = {
            'api_key': settings.DISCOURSE_API_KEY,
            'api_username': settings.DISCOURSE_API_USERNAME,
        }
        silent = kwargs.pop('silent', False)
        if args:
            endpoint['parsed_url'] = endpoint['path'] % args
        else:
            endpoint['parsed_url'] = endpoint['path']
        data = {}
        for arg in endpoint['args']['required']:
            data[arg] = kwargs[arg]
        for arg in endpoint['args']['optional']:
            if arg in kwargs:
                data[arg] = kwargs[arg]
        for arg in kwargs:
            if arg not in endpoint['args']['required'] and arg not in endpoint['args']['optional'] and not silent:
                logger.warn("Received unrecognized kwarg %s for endpoint %s" % (arg, endpoint))
        r = endpoint['method'](settings.DISCOURSE_URL + endpoint['parsed_url'], params=params, json=data)
        try:
            if 'errors' in r.json() and not silent:
                logger.error("Discourse execution failed.\nEndpoint: %s\nErrors: %s" % (endpoint, r.json()['errors']))
                raise DiscourseError(endpoint, r.json()['errors'])
            if 'success' in r.json():
                if not r.json()['success'] and not silent:
                    raise DiscourseError(endpoint, None)
            out = r.json()
        except ValueError:
            out = r.text
        finally:
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise DiscourseError(endpoint, e.response.status_code)
        return out

    @staticmethod
    def __generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def __get_groups():
        endpoint = ENDPOINTS['groups']['list']
        data = DiscourseManager.__exc(endpoint)
        return [g for g in data if not g['automatic']]

    @staticmethod
    def __update_group_cache():
        GroupCache.objects.filter(service="discourse").delete()
        cache = GroupCache.objects.create(service="discourse")
        cache.groups = json.dumps(DiscourseManager.__get_groups())
        cache.save()
        return cache

    @staticmethod
    def __get_group_cache():
        if not GroupCache.objects.filter(service="discourse").exists():
            DiscourseManager.__update_group_cache()
        cache = GroupCache.objects.get(service="discourse")
        age = timezone.now() - cache.created
        if age > DiscourseManager.GROUP_CACHE_MAX_AGE:
            logger.debug("Group cache has expired. Triggering update.")
            cache = DiscourseManager.__update_group_cache()
        return json.loads(cache.groups)

    @staticmethod
    def __create_group(name):
        endpoint = ENDPOINTS['groups']['create']
        DiscourseManager.__exc(endpoint, name=name[:20], visible=True)
        DiscourseManager.__update_group_cache()

    @staticmethod
    def __group_name_to_id(name):
        cache = DiscourseManager.__get_group_cache()
        for g in cache:
            if g['name'] == name[0:20]:
                return g['id']
        logger.debug("Group %s not found on Discourse. Creating" % name)
        DiscourseManager.__create_group(name)
        return DiscourseManager.__group_name_to_id(name)

    @staticmethod
    def __group_id_to_name(id):
        cache = DiscourseManager.__get_group_cache()
        for g in cache:
            if g['id'] == id:
                return g['name']
        raise KeyError("Group ID %s not found on Discourse" % id)

    @staticmethod
    def __add_user_to_group(id, username):
        endpoint = ENDPOINTS['groups']['add_user']
        DiscourseManager.__exc(endpoint, id, usernames=[username])

    @staticmethod
    def __remove_user_from_group(id, username):
        endpoint = ENDPOINTS['groups']['remove_user']
        DiscourseManager.__exc(endpoint, id, username=username)

    @staticmethod
    def __generate_group_dict(names):
        group_dict = {}
        for name in names:
            group_dict[name] = DiscourseManager.__group_name_to_id(name)
        return group_dict

    @staticmethod
    def __get_user_groups(username):
        data = DiscourseManager.__get_user(username)
        return [g['id'] for g in data['user']['groups'] if not g['automatic']]

    @staticmethod
    def __user_name_to_id(name, silent=False):
        data = DiscourseManager.__get_user(name, silent=silent)
        return data['user']['id']

    @staticmethod
    def __user_id_to_name(id):
        raise NotImplementedError

    @staticmethod
    def __get_user(username, silent=False):
        endpoint = ENDPOINTS['users']['get']
        return DiscourseManager.__exc(endpoint, username, silent=silent)

    @staticmethod
    def __activate_user(username):
        endpoint = ENDPOINTS['users']['activate']
        id = DiscourseManager.__user_name_to_id(username)
        DiscourseManager.__exc(endpoint, id)

    @staticmethod
    def __update_user(username, **kwargs):
        endpoint = ENDPOINTS['users']['update']
        id = DiscourseManager.__user_name_to_id(username)
        DiscourseManager.__exc(endpoint, id, params=kwargs)

    @staticmethod
    def __create_user(username, email, password):
        endpoint = ENDPOINTS['users']['create']
        DiscourseManager.__exc(endpoint, name=username, username=username, email=email, password=password, active=True)

    @staticmethod
    def __check_if_user_exists(username):
        try:
            DiscourseManager.__user_name_to_id(username, silent=True)
            return True
        except:
            return False

    @staticmethod
    def __suspend_user(username):
        id = DiscourseManager.__user_name_to_id(username)
        endpoint = ENDPOINTS['users']['suspend']
        return DiscourseManager.__exc(endpoint, id, duration=DiscourseManager.SUSPEND_DAYS,
                                      reason=DiscourseManager.SUSPEND_REASON)

    @staticmethod
    def __unsuspend(username):
        id = DiscourseManager.__user_name_to_id(username)
        endpoint = ENDPOINTS['users']['unsuspend']
        return DiscourseManager.__exc(endpoint, id)

    @staticmethod
    def __set_email(username, email):
        endpoint = ENDPOINTS['users']['set_email']
        return DiscourseManager.__exc(endpoint, username, email=email)

    @staticmethod
    def __logout(id):
        endpoint = ENDPOINTS['users']['logout']
        return DiscourseManager.__exc(endpoint, id)

    @staticmethod
    def __get_user_by_external(id):
        endpoint = ENDPOINTS['users']['external']
        return DiscourseManager.__exc(endpoint, id)

    @staticmethod
    def __user_id_by_external_id(id):
        data = DiscourseManager.__get_user_by_external(id)
        return data['user']['id']

    @staticmethod
    def _sanitize_username(username):
        sanitized = username.replace(" ", "_")
        sanitized = sanitized.strip(' _')
        sanitized = sanitized.replace("'", "")
        return sanitized

    @staticmethod
    def _sanitize_groupname(name):
        name = name.strip(' _')
        name = re.sub('[^\w]', '', name)
        if len(name) < 3:
            name = name + "".join('_' for i in range(3-len(name)))
        return name[:20]

    @staticmethod
    def update_groups(user):
        groups = []
        for g in user.groups.all():
            groups.append(DiscourseManager._sanitize_groupname(str(g)[:20]))
        logger.debug("Updating discourse user %s groups to %s" % (user, groups))
        group_dict = DiscourseManager.__generate_group_dict(groups)
        inv_group_dict = {v: k for k, v in group_dict.items()}
        username = DiscourseManager.__get_user_by_external(user.pk)['user']['username']
        user_groups = DiscourseManager.__get_user_groups(username)
        add_groups = [group_dict[x] for x in group_dict if not group_dict[x] in user_groups]
        rem_groups = [x for x in user_groups if not x in inv_group_dict]
        if add_groups or rem_groups:
            logger.info(
                "Updating discourse user %s groups: adding %s, removing %s" % (username, add_groups, rem_groups))
            for g in add_groups:
                DiscourseManager.__add_user_to_group(g, username)
            for g in rem_groups:
                DiscourseManager.__remove_user_from_group(g, username)

    @staticmethod
    def disable_user(user):
        logger.debug("Disabling user %s Discourse access." % user)
        d_user = DiscourseManager.__get_user_by_external(user.pk)
        DiscourseManager.__logout(d_user['user']['id'])
        DiscourseManager.__suspend_user(d_user['user']['username'])
        logger.info("Disabled user %s Discourse access." % user)
        return True
