from __future__ import unicode_literals
import random
import string
import requests
import hashlib
from eveonline.managers import EveManager
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from six import iteritems

import logging

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
        return None

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
    def disable_user(cls, username):
        """ Disable user """
        ret = cls.exec_request('user/{}'.format(username), 'put', active=0)
        logger.debug(ret)
        ret = cls.exec_request('user/{}'.format(username), 'put', email="")
        logger.debug(ret)
        if cls._response_ok(ret):
            try:
                cls.update_roles(username, [])
                logger.info("Disabled SeAT user with username %s" % username)
                return username
            except KeyError:
                # if something goes wrong, delete user from seat instead of disabling
                if cls.delete_user(username):
                    return username
        logger.info("Failed to disabled SeAT user with username %s" % username)
        return None

    @classmethod
    def enable_user(cls, username):
        """ Enable user """
        ret = cls.exec_request('user/{}'.format(username), 'put', active=1)
        logger.debug(ret)
        if cls._response_ok(ret):
            logger.info("Enabled SeAT user with username %s" % username)
            return username
        logger.info("Failed to enabled SeAT user with username %s" % username)
        return None

    @classmethod
    def update_user(cls, username, email, password):
        """ Edit user info """
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
    def synchronize_eveapis(cls, user=None):

        # Fetch all of the API keys stored in SeAT already
        seat_all_keys = cls.get_all_seat_eveapis()

        # retrieve only user-specific api keys if user is specified
        if user:
            keypairs = EveManager.get_api_key_pairs(user)
        else:
            # retrieve all api keys instead
            keypairs = EveManager.get_all_api_key_pairs()

        for keypair in keypairs:
            # Transfer the key if it isn't already in SeAT
            if keypair.api_id not in seat_all_keys.keys():
                # Add new keys
                logger.debug("Adding Api Key with ID %s" % keypair.api_id)
                try:
                    ret = cls.exec_request('key', 'post',
                                           key_id=keypair.api_id,
                                           v_code=keypair.api_key,
                                           raise_for_status=True)
                    logger.debug(ret)
                except requests.HTTPError as e:
                    if e.response.status_code == 400:
                        logger.debug("API key already exists")
                    else:
                        logger.exception("API key sync failed")
                        continue  # Skip the rest of the key processing
            else:
                # remove it from the list so it doesn't get deleted in the last step
                seat_all_keys.pop(keypair.api_id)

            # Attach API key to the users SeAT account, if possible
            try:
                userinfo = cache.get_or_set('seat_user_status_' + cls.username_hash(keypair.user.seat.username),
                                            lambda: cls.check_user_status(keypair.user.seat.username),
                                            300)  # Cache for 5 minutes

                if not bool(userinfo):
                    # No SeAT account, skip
                    logger.debug("Could not find users SeAT id, cannot assign key to them")
                    continue

                # If the user has activated seat, assign the key to them
                logger.debug("Transferring Api Key with ID %s to user %s with ID %s " % (
                    keypair.api_id,
                    keypair.user.seat.username,
                    userinfo['id']))
                ret = cls.exec_request('key/transfer/{}/{}'.format(keypair.api_id, userinfo['id']),
                                       'get')
                logger.debug(ret)
            except ObjectDoesNotExist:
                logger.debug("User does not have SeAT activated, could not assign key to user")

        if bool(seat_all_keys) and not user and getattr(settings, 'SEAT_PURGE_DELETED', False):
            # remove from SeAT keys that were removed from Auth
            for key, key_user in iteritems(seat_all_keys):
                # Remove the key only if it is an account or character key
                ret = cls.exec_request('key/{}'.format(key), 'get')
                logger.debug(ret)
                try:
                    if (ret['info']['type'] == "Account") or (ret['info']['type'] == "Character"):
                        logger.debug("Removing api key %s from SeAT database" % key)
                        ret = cls.exec_request('key/{}'.format(key), 'delete')
                        logger.debug(ret)
                except KeyError:
                    pass

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
        m.update(username)
        return m.hexdigest()
