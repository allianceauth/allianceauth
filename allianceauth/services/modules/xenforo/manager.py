import random
import string
import requests
import json

from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class XenForoManager:
    def __init__(self):
        if not settings.XENFORO_ENDPOINT:
            logger.debug("Could not find XenForo endpoint")
        if not settings.XENFORO_APIKEY:
            logger.debug("XenForo API Key not found")
        pass

    @staticmethod
    def __sanitize_username(username):
        sanitized = username.replace(" ", "_")
        return sanitized

    @staticmethod
    def __generate_password():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def exec_http_request(http_params):
        default_params = {
            'hash': settings.XENFORO_APIKEY
        }
        http_params.update(default_params)
        r = requests.get(settings.XENFORO_ENDPOINT, params=http_params)
        return r

    @staticmethod
    def add_user(username, email):

        sanitized = XenForoManager.__sanitize_username(username)
        password = XenForoManager.__generate_password()

        data = {
            'action': 'register',
            'username': sanitized,
            'password': password,
            'email': email,
            'group': settings.XENFORO_DEFAULT_GROUP,
            'visible': '1',
            'user_state': 'valid'
        }

        r = XenForoManager.exec_http_request(data)

        # check if the user already exist but was disabled
        if r.status_code != 200:
            if json.loads(r.text)['error'] == 7:
                data = XenForoManager.reactivate_user(sanitized)
                return data

        response = {
            'response': {
                'message': r.text,
                'status_code': r.status_code
            }
        }
        data.update(response)
        return data

    @staticmethod
    def reset_password(username):

        password = XenForoManager.__generate_password()

        data = {
            'action': 'editUser',
            'user': username,
            'password': password
        }

        r = XenForoManager.exec_http_request(data)

        response = {
            'response': {
                'message': r.text,
                'status_code': r.status_code
            }
        }
        data.update(response)
        return data

    @staticmethod
    def disable_user(username):
        data = {
            'action': 'editUser',
            'user': username,
            'remove_groups': settings.XENFORO_DEFAULT_GROUP
        }
        r = XenForoManager.exec_http_request(data)
        return r

    @staticmethod
    def reactivate_user(username):
        data = {
            'action': 'editUser',
            'user': username,
            'add_groups': settings.XENFORO_DEFAULT_GROUP,
            'password': XenForoManager.__generate_password()
        }
        r = XenForoManager.exec_http_request(data)
        response = {
            'response': {
                'message': r.text,
                'status_code': r.status_code
            },
            'username': username
        }
        data.update(response)
        return data

    @staticmethod
    def update_user_password(username, raw_password):
        data = {
            'action': 'editUser',
            'user': username,
            'password': raw_password
        }
        r = XenForoManager.exec_http_request(data)
        response = {
            'response': {
                'message': r.text,
                'status_code': r.status_code
            },
            'username': username
        }
        data.update(response)
        return data
