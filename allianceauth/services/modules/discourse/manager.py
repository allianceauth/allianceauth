import logging
import requests
import re
from django.conf import settings
from django.core.cache import cache
from hashlib import md5

logger = logging.getLogger(__name__)

GROUP_CACHE_MAX_AGE = getattr(settings, 'DISCOURSE_GROUP_CACHE_MAX_AGE', 2 * 60 * 60)  # default 2 hours


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
            'path': "/groups/search.json",
            'method': 'get',
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'create': {
            'path': "/admin/groups",
            'method': 'post',
            'args': {
                'required': ['name'],
                'optional': ['visible'],
            }
        },
        'add_user': {
            'path': "/admin/groups/%s/members.json",
            'method': 'put',
            'args': {
                'required': ['usernames'],
                'optional': [],
            },
        },
        'remove_user': {
            'path': "/admin/groups/%s/members.json",
            'method': 'delete',
            'args': {
                'required': ['username'],
                'optional': [],
            },
        },
        'delete': {
            'path': "/admin/groups/%s.json",
            'method': 'delete',
            'args': {
                'required': [],
                'optional': [],
            },
        },
    },
    'users': {
        'create': {
            'path': "/users",
            'method': 'post',
            'args': {
                'required': ['name', 'email', 'password', 'username'],
                'optional': ['active'],
            },
        },
        'update': {
            'path': "/users/%s.json",
            'method': 'put',
            'args': {
                'required': ['params'],
                'optional': [],
            }
        },
        'get': {
            'path': "/users/%s.json",
            'method': 'get',
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'activate': {
            'path': "/admin/users/%s/activate",
            'method': 'put',
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'set_email': {
            'path': "/users/%s/preferences/email",
            'method': 'put',
            'args': {
                'required': ['email'],
                'optional': [],
            },
        },
        'suspend': {
            'path': "/admin/users/%s/suspend",
            'method': 'put',
            'args': {
                'required': ['duration', 'reason'],
                'optional': [],
            },
        },
        'unsuspend': {
            'path': "/admin/users/%s/unsuspend",
            'method': 'put',
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'logout': {
            'path': "/admin/users/%s/log_out",
            'method': 'post',
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'external': {
            'path': "/users/by-external/%s.json",
            'method': 'get',
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

    REVOKED_EMAIL = 'revoked@localhost'
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
        r = getattr(requests, endpoint['method'])(settings.DISCOURSE_URL + endpoint['parsed_url'], params=params,
                                                  json=data)
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
    def _get_groups():
        endpoint = ENDPOINTS['groups']['list']
        data = DiscourseManager.__exc(endpoint)
        return [g for g in data if not g['automatic']]

    @staticmethod
    def _create_group(name):
        endpoint = ENDPOINTS['groups']['create']
        return DiscourseManager.__exc(endpoint, name=name[:20], visible=True)['basic_group']

    @staticmethod
    def _generate_cache_group_name_key(name):
        return 'DISCOURSE_GROUP_NAME__%s' % md5(name.encode('utf-8')).hexdigest()

    @staticmethod
    def _generate_cache_group_id_key(g_id):
        return 'DISCOURSE_GROUP_ID__%s' % g_id

    @staticmethod
    def __group_name_to_id(name):
        name = DiscourseManager._sanitize_groupname(name)

        def get_or_create_group():
            groups = DiscourseManager._get_groups()
            for g in groups:
                if g['name'].lower() == name.lower():
                    return g['id']
            return DiscourseManager._create_group(name)['id']

        return cache.get_or_set(DiscourseManager._generate_cache_group_name_key(name), get_or_create_group,
                                GROUP_CACHE_MAX_AGE)

    @staticmethod
    def __group_id_to_name(g_id):
        def get_group_name():
            groups = DiscourseManager._get_groups()
            for g in groups:
                if g['id'] == g_id:
                    return g['name']
            raise KeyError("Group ID %s not found on Discourse" % g_id)

        return cache.get_or_set(DiscourseManager._generate_cache_group_id_key(g_id), get_group_name,
                                GROUP_CACHE_MAX_AGE)

    @staticmethod
    def __add_user_to_group(g_id, username):
        endpoint = ENDPOINTS['groups']['add_user']
        DiscourseManager.__exc(endpoint, g_id, usernames=[username])

    @staticmethod
    def __remove_user_from_group(g_id, username):
        endpoint = ENDPOINTS['groups']['remove_user']
        DiscourseManager.__exc(endpoint, g_id, username=username)

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
    def __get_user(username, silent=False):
        endpoint = ENDPOINTS['users']['get']
        return DiscourseManager.__exc(endpoint, username, silent=silent)

    @staticmethod
    def __activate_user(username):
        endpoint = ENDPOINTS['users']['activate']
        u_id = DiscourseManager.__user_name_to_id(username)
        DiscourseManager.__exc(endpoint, u_id)

    @staticmethod
    def __update_user(username, **kwargs):
        endpoint = ENDPOINTS['users']['update']
        u_id = DiscourseManager.__user_name_to_id(username)
        DiscourseManager.__exc(endpoint, u_id, params=kwargs)

    @staticmethod
    def __create_user(username, email, password):
        endpoint = ENDPOINTS['users']['create']
        DiscourseManager.__exc(endpoint, name=username, username=username, email=email, password=password, active=True)

    @staticmethod
    def __check_if_user_exists(username):
        try:
            DiscourseManager.__user_name_to_id(username, silent=True)
            return True
        except DiscourseError:
            return False

    @staticmethod
    def __suspend_user(username):
        u_id = DiscourseManager.__user_name_to_id(username)
        endpoint = ENDPOINTS['users']['suspend']
        return DiscourseManager.__exc(endpoint, u_id, duration=DiscourseManager.SUSPEND_DAYS,
                                      reason=DiscourseManager.SUSPEND_REASON)

    @staticmethod
    def __unsuspend(username):
        u_id = DiscourseManager.__user_name_to_id(username)
        endpoint = ENDPOINTS['users']['unsuspend']
        return DiscourseManager.__exc(endpoint, u_id)

    @staticmethod
    def __set_email(username, email):
        endpoint = ENDPOINTS['users']['set_email']
        return DiscourseManager.__exc(endpoint, username, email=email)

    @staticmethod
    def __logout(u_id):
        endpoint = ENDPOINTS['users']['logout']
        return DiscourseManager.__exc(endpoint, u_id)

    @staticmethod
    def __get_user_by_external(u_id):
        endpoint = ENDPOINTS['users']['external']
        return DiscourseManager.__exc(endpoint, u_id)

    @staticmethod
    def __user_id_by_external_id(u_id):
        data = DiscourseManager.__get_user_by_external(u_id)
        return data['user']['id']

    @staticmethod
    def _sanitize_name(name):
        name = name.replace(' ', '_')
        name = name.replace("'", '')
        name = name.lstrip(' _')
        name = name[:20]
        name = name.rstrip(' _')
        return name

    @staticmethod
    def _sanitize_username(username):
        return DiscourseManager._sanitize_name(username)

    @staticmethod
    def _sanitize_groupname(name):
        name = re.sub('[^\w]', '', name)
        name = DiscourseManager._sanitize_name(name)
        if len(name) < 3:
            name = "Group " + name
        return name

    @staticmethod
    def update_groups(user):
        groups = [DiscourseManager._sanitize_groupname(user.profile.state.name)]
        for g in user.groups.all():
            groups.append(DiscourseManager._sanitize_groupname(str(g)))
        logger.debug("Updating discourse user %s groups to %s" % (user, groups))
        group_dict = DiscourseManager.__generate_group_dict(groups)
        inv_group_dict = {v: k for k, v in group_dict.items()}
        username = DiscourseManager.__get_user_by_external(user.pk)['user']['username']
        user_groups = DiscourseManager.__get_user_groups(username)
        add_groups = [group_dict[x] for x in group_dict if not group_dict[x] in user_groups]
        rem_groups = [x for x in user_groups if x not in inv_group_dict]
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
        logger.info("Disabled user %s Discourse access." % user)
        return True
