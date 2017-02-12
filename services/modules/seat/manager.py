from __future__ import unicode_literals
import random
import string
import requests
from eveonline.managers import EveManager
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from six import iteritems

import logging

logger = logging.getLogger(__name__)


class SeatManager:
    def __init__(self):
        pass

    RESPONSE_OK = 'ok'

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @classmethod
    def _response_ok(cls, response):
        return cls.RESPONSE_OK in response

    @staticmethod
    def exec_request(endpoint, func, **kwargs):
        """ Send an https api request """
        try:
            endpoint = '{0}/api/v1/{1}'.format(settings.SEAT_URL, endpoint)
            headers = {'X-Token': settings.SEAT_XTOKEN, 'Accept': 'application/json'}
            logger.debug(headers)
            logger.debug(endpoint)
            ret = getattr(requests, func)(endpoint, headers=headers, data=kwargs)
            ret.raise_for_status()
            return ret.json()
        except:
            logger.exception("Error encountered while performing API request to SeAT with url {}".format(endpoint))
            return {}

    @classmethod
    def add_user(cls, username, email):
        """ Add user to service """
        sanatized = str(SeatManager.__santatize_username(username))
        logger.debug("Adding user to SeAT with username %s" % sanatized)
        password = SeatManager.__generate_random_pass()
        ret = SeatManager.exec_request('user', 'post', username=sanatized, email=str(email), password=password)
        logger.debug(ret)
        if cls._response_ok(ret):
            logger.info("Added SeAT user with username %s" % sanatized)
            return sanatized, password
        logger.info("Failed to add SeAT user with username %s" % sanatized)
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
        ret = SeatManager.exec_request('user/{}'.format(username), 'put', active=1)
        logger.debug(ret)
        if cls._response_ok(ret):
            logger.info("Enabled SeAT user with username %s" % username)
            return username
        logger.info("Failed to enabled SeAT user with username %s" % username)
        return None

    @classmethod
    def update_user(cls, username, email, password):
        """ Edit user info """
        logger.debug("Updating SeAT username %s with email %s and password hash starting with %s" % (username, email,
                                                                                                     password[0:5]))
        ret = SeatManager.exec_request('user/{}'.format(username), 'put', email=email)
        logger.debug(ret)
        if not cls._response_ok(ret):
            logger.warn("Failed to update email for username {}".format(username))
        ret = SeatManager.exec_request('user/{}'.format(username), 'put', password=password)
        logger.debug(ret)
        if not cls._response_ok(ret):
            logger.warn("Failed to update password for username {}".format(username))
            return None
        logger.info("Updated SeAT user with username %s" % username)
        return username

    @staticmethod
    def update_user_password(username, email, plain_password=None):
        logger.debug("Settings new SeAT password for user %s" % username)
        if not plain_password:
            plain_password = SeatManager.__generate_random_pass()
        if SeatManager.update_user(username, email, plain_password):
            return plain_password

    @staticmethod
    def check_user_status(username):
        sanatized = str(SeatManager.__santatize_username(username))
        logger.debug("Checking SeAT status for user %s" % sanatized)
        ret = SeatManager.exec_request('user/{}'.format(sanatized), 'get')
        logger.debug(ret)
        return ret

    @staticmethod
    def get_all_seat_eveapis():
        seat_all_keys = SeatManager.exec_request('key', 'get')
        seat_keys = {}
        for key in seat_all_keys:
            try:
                seat_keys[key["key_id"]] = key["user_id"]
            except KeyError:
                seat_keys[key["key_id"]] = None
        return seat_keys


    @staticmethod
    def synchronize_eveapis(user=None):
        seat_all_keys = SeatManager.get_all_seat_eveapis()
        userinfo = None
        # retrieve only user-specific api keys if user is specified
        if user:
            keypars = EveManager.get_api_key_pairs(user)
            try:
                userinfo = SeatManager.check_user_status(user.seat.username)
            except ObjectDoesNotExist:
                pass
        else:
            # retrieve all api keys instead
            keypars = EveManager.get_all_api_key_pairs()
        if keypars:
            for keypar in keypars:
                if keypar.api_id not in seat_all_keys.keys():
                    #Add new keys
                    logger.debug("Adding Api Key with ID %s" % keypar.api_id)
                    ret = SeatManager.exec_request('key', 'post', key_id=keypar.api_id, v_code=keypar.api_key)
                    logger.debug(ret)
                else:
                    # remove it from the list so it doesn't get deleted in the last step
                    seat_all_keys.pop(keypar.api_id)
                if not userinfo:  # TODO: should the following be done only for new keys?
                    # Check the key's user status
                    logger.debug("Retrieving user name from Auth's SeAT users database")
                    try:
                        if keypar.user.seat.username:
                            logger.debug("Retrieving user %s info from SeAT users database" % keypar.user.seat.username)
                            userinfo = SeatManager.check_user_status(keypar.user.seat.username)
                    except ObjectDoesNotExist:
                        pass
                if userinfo:
                    try:
                        # If the user has activated seat, assign the key to him.
                        logger.debug("Transferring Api Key with ID %s to user %s with ID %s " % (
                            keypar.api_id,
                            keypar.user.seat.username,
                            userinfo['id']))
                        ret = SeatManager.exec_request('key/transfer/{}/{}'.format(keypar.api_id, userinfo['id']),
                                                       'get')
                        logger.debug(ret)
                    except ObjectDoesNotExist:
                        logger.debug("User does not have SeAT activated, could not assign key to user")

        if bool(seat_all_keys) and not user and hasattr(settings, 'SEAT_PURGE_DELETED') and settings.SEAT_PURGE_DELETED:
            # remove from SeAT keys that were removed from Auth
            for key, key_user in iteritems(seat_all_keys):
                # Remove the key only if it is an account or character key
                ret = SeatManager.exec_request('key/{}'.format(key), 'get')
                logger.debug(ret)
                try:
                    if (ret['info']['type'] == "Account") or (ret['info']['type'] == "Character"):
                        logger.debug("Removing api key %s from SeAT database" % key)
                        ret = SeatManager.exec_request('key/{}'.format(key), 'delete')
                        logger.debug(ret)
                except KeyError:
                    pass

    @staticmethod
    def get_all_roles():
        groups = {}
        ret = SeatManager.exec_request('role', 'get')
        logger.debug(ret)
        for group in ret:
            groups[group["title"]] = group["id"]
        logger.debug("Retrieved role list from SeAT: %s" % str(groups))
        return groups

    @staticmethod
    def add_role(role):
        ret = SeatManager.exec_request('role/new', 'post', name=role)
        logger.debug(ret)
        logger.info("Added Seat group %s" % role)
        role_info = SeatManager.exec_request('role/detail/{}'.format(role), 'get')
        logger.debug(role_info)
        return role_info["id"]

    @staticmethod
    def add_role_to_user(user_id, role_id):
        ret = SeatManager.exec_request('role/grant-user-role/{}/{}'.format(user_id, role_id), 'get')
        logger.info("Added role %s to user %s" % (role_id, user_id))
        return ret

    @staticmethod
    def revoke_role_from_user(user_id, role_id):
        ret = SeatManager.exec_request('role/revoke-user-role/{}/{}'.format(user_id, role_id), 'get')
        logger.info("Revoked role %s from user %s" % (role_id, user_id))
        return ret

    @staticmethod
    def update_roles(seat_user, roles):
        logger.debug("Updating SeAT user %s with roles %s" % (seat_user, roles))
        user_info = SeatManager.check_user_status(seat_user)
        user_roles = {}
        if type(user_info["roles"]) is list:
            for role in user_info["roles"]:
                user_roles[role["title"]] = role["id"]
        logger.debug("Got user %s SeAT roles %s" % (seat_user, user_roles))
        seat_roles = SeatManager.get_all_roles()
        addroles = set(roles) - set(user_roles.keys())
        remroles = set(user_roles.keys()) - set(roles)

        logger.info("Updating SeAT roles for user %s - adding %s, removing %s" % (seat_user, addroles, remroles))
        for r in addroles:
            if r not in seat_roles:
                seat_roles[r] = SeatManager.add_role(r)
            logger.debug("Adding role %s to SeAT user %s" % (r, seat_user))
            SeatManager.add_role_to_user(user_info["id"], seat_roles[r])
        for r in remroles:
            logger.debug("Removing role %s from user %s" % (r, seat_user))
            SeatManager.revoke_role_from_user(user_info["id"], seat_roles[r])
