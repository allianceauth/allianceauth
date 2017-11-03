import hashlib
import logging
import random
import string

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SeatManager:
    def __init__(self):
        pass

    RESPONSE_OK = 'ok'

    @staticmethod
    def __sanitize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @classmethod
    def _response_ok(cls, response):
        return cls.RESPONSE_OK in response

    @staticmethod
    def exec_request(endpoint, func, raise_for_status=False, **kwargs):
        """ Send an https api request """
        try:
            endpoint = '{0}/api/v1/{1}'.format(settings.SEAT_URL, endpoint)
            headers = {'X-Token': settings.SEAT_XTOKEN, 'Accept': 'application/json'}
            logger.debug(headers)
            logger.debug(endpoint)
            ret = getattr(requests, func)(endpoint, headers=headers, data=kwargs)
            ret.raise_for_status()
            return ret.json()
        except requests.HTTPError as e:
            if raise_for_status:
                raise e
            logger.exception("Error encountered while performing API request to SeAT with url {}".format(endpoint))
            return {}

    @classmethod
    def add_user(cls, username, email):
        """ Add user to service """
        sanitized = str(cls.__sanitize_username(username))
        logger.debug("Adding user to SeAT with username %s" % sanitized)
        password = cls.__generate_random_pass()
        ret = cls.exec_request('user', 'post', username=sanitized, email=str(email), password=password)
        logger.debug(ret)
        if cls._response_ok(ret):
            logger.info("Added SeAT user with username %s" % sanitized)
            return sanitized, password
        logger.info("Failed to add SeAT user with username %s" % sanitized)
        return None, None

    @classmethod
    def delete_user(cls, username):
        """ Delete user """
        ret = cls.exec_request('user/{}'.format(username), 'delete')
        logger.debug(ret)
        if cls._response_ok(ret):
            logger.info("Deleted SeAT user with username %s" % username)
            return username
        return None

    @classmethod
    def enable_user(cls, username):
        """ Enable user """
        ret = cls.exec_request('user/{}'.format(username), 'put', account_status=1)
        logger.debug(ret)
        if cls._response_ok(ret):
            logger.info("Enabled SeAT user with username %s" % username)
            return username
        logger.info("Failed to enabled SeAT user with username %s" % username)
        return None

    @classmethod
    def disable_user(cls, username):
        """ Disable user """
        cls.update_roles(username, [])
        ret = cls.exec_request('user/{}'.format(username), 'put', account_status=0)
        logger.debug(ret)
        if cls._response_ok(ret):
            logger.info("Disabled SeAT user with username %s" % username)
            return username
        logger.info("Failed to disable SeAT user with username %s" % username)
        return None

    @classmethod
    def _check_email_changed(cls, username, email):
        """Compares email to one set on SeAT"""
        ret = cls.exec_request('user/{}'.format(username), 'get', raise_for_status=True)
        return ret['email'] != email

    @classmethod
    def update_user(cls, username, email, password):
        """ Edit user info """
        if cls._check_email_changed(username, email):
            # if we try to set the email to whatever it is already on SeAT, we get a HTTP422 error
            logger.debug("Updating SeAT username %s with email %s and password" % (username, email))
            ret = cls.exec_request('user/{}'.format(username), 'put', email=email)
            logger.debug(ret)
            if not cls._response_ok(ret):
                logger.warn("Failed to update email for username {}".format(username))
        ret = cls.exec_request('user/{}'.format(username), 'put', password=password)
        logger.debug(ret)
        if not cls._response_ok(ret):
            logger.warn("Failed to update password for username {}".format(username))
            return None
        logger.info("Updated SeAT user with username %s" % username)
        return username

    @classmethod
    def update_user_password(cls, username, email, plain_password=None):
        logger.debug("Settings new SeAT password for user %s" % username)
        if not plain_password:
            plain_password = cls.__generate_random_pass()
        if cls.update_user(username, email, plain_password):
            return plain_password

    @classmethod
    def check_user_status(cls, username):
        sanitized = str(cls.__sanitize_username(username))
        logger.debug("Checking SeAT status for user %s" % sanitized)
        ret = cls.exec_request('user/{}'.format(sanitized), 'get')
        logger.debug(ret)
        return ret

    @classmethod
    def get_all_seat_eveapis(cls):
        seat_all_keys = cls.exec_request('key', 'get')
        seat_keys = {}
        for key in seat_all_keys:
            try:
                seat_keys[key["key_id"]] = key["user_id"]
            except KeyError:
                seat_keys[key["key_id"]] = None
        return seat_keys

    @classmethod
    def get_all_roles(cls):
        groups = {}
        ret = cls.exec_request('role', 'get')
        logger.debug(ret)
        for group in ret:
            groups[group["title"]] = group["id"]
        logger.debug("Retrieved role list from SeAT: %s" % str(groups))
        return groups

    @classmethod
    def add_role(cls, role):
        ret = cls.exec_request('role/new', 'post', name=role)
        logger.debug(ret)
        logger.info("Added Seat group %s" % role)
        role_info = cls.exec_request('role/detail/{}'.format(role), 'get')
        logger.debug(role_info)
        return role_info["id"]

    @classmethod
    def add_role_to_user(cls, user_id, role_id):
        ret = cls.exec_request('role/grant-user-role/{}/{}'.format(user_id, role_id), 'get')
        logger.info("Added role %s to user %s" % (role_id, user_id))
        return ret

    @classmethod
    def revoke_role_from_user(cls, user_id, role_id):
        ret = cls.exec_request('role/revoke-user-role/{}/{}'.format(user_id, role_id), 'get')
        logger.info("Revoked role %s from user %s" % (role_id, user_id))
        return ret

    @classmethod
    def update_roles(cls, seat_user, roles):
        logger.debug("Updating SeAT user %s with roles %s" % (seat_user, roles))
        user_info = cls.check_user_status(seat_user)
        user_roles = {}
        if type(user_info["roles"]) is list:
            for role in user_info["roles"]:
                user_roles[role["title"]] = role["id"]
        logger.debug("Got user %s SeAT roles %s" % (seat_user, user_roles))
        seat_roles = cls.get_all_roles()
        addroles = set(roles) - set(user_roles.keys())
        remroles = set(user_roles.keys()) - set(roles)

        logger.info("Updating SeAT roles for user %s - adding %s, removing %s" % (seat_user, addroles, remroles))
        for r in addroles:
            if r not in seat_roles:
                seat_roles[r] = cls.add_role(r)
            logger.debug("Adding role %s to SeAT user %s" % (r, seat_user))
            cls.add_role_to_user(user_info["id"], seat_roles[r])
        for r in remroles:
            logger.debug("Removing role %s from user %s" % (r, seat_user))
            cls.revoke_role_from_user(user_info["id"], seat_roles[r])

    @staticmethod
    def username_hash(username):
        m = hashlib.sha1()
        m.update(username.encode('utf-8'))
        return m.hexdigest()
