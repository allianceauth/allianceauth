from __future__ import unicode_literals
import random
import string
import re
from hashlib import md5
try:
    from xmlrpclib import Server
except ImportError:
    # python 3
    from xmlrpc import server as Server


from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class IPBoardManager:
    def __init__(self):
        pass

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def _gen_pwhash(password):
        return md5(password.encode('utf-8')).hexdigest()

    @staticmethod
    def _sanitize_groupname(name):
        name = name.strip(' _')
        return re.sub('[^\w.-]', '', name)

    @staticmethod
    def exec_xmlrpc(func, **kwargs):
        """ Send a XMLRPC request """
        try:
            server = Server(settings.IPBOARD_ENDPOINT, verbose=False)
            params = {}
            for i in kwargs:
                params[i] = kwargs[i]
            params['api_key'] = settings.IPBOARD_APIKEY
            params['api_module'] = settings.IPBOARD_APIMODULE

            return getattr(server, func)(params)
        except:
            return {}

    @classmethod
    def add_user(cls, username, email):
        """ Add user to service """
        sanatized = str(IPBoardManager.__santatize_username(username))
        logger.debug("Adding user to IPBoard with username %s" % sanatized)
        plain_password = IPBoardManager.__generate_random_pass()
        password = cls._gen_pwhash(plain_password)
        IPBoardManager.exec_xmlrpc('createUser', username=sanatized, email=str(email), display_name=sanatized,
                                   md5_passwordHash=password)
        logger.info("Added IPBoard user with username %s" % sanatized)
        return sanatized, plain_password

    @staticmethod
    def delete_user(username):
        """ Delete user """
        IPBoardManager.exec_xmlrpc('deleteUser', username=username)
        logger.info("Deleted IPBoard user with username %s" % username)
        return username

    @staticmethod
    def disable_user(username):
        """ Disable user """
        IPBoardManager.exec_xmlrpc('disableUser', username=username)
        logger.info("Disabled IPBoard user with username %s" % username)
        return username

    @classmethod
    def update_user(cls, username, email, password):
        """ Add user to service """
        password = cls._gen_pwhash(password)
        logger.debug("Updating IPBoard username %s with email %s and password hash starting with %s" % (
            username, email, password[0:5]))
        IPBoardManager.exec_xmlrpc('updateUser', username=username, email=email, md5_passwordHash=password)
        logger.info("Updated IPBoard user with username %s" % username)
        return username

    @staticmethod
    def get_all_groups():
        groups = []
        ret = IPBoardManager.exec_xmlrpc('getAllGroups')
        for group in ret:
            groups.append(group["g_title"])
        logger.debug("Retrieved group list from IPBoard: %s" % groups)
        return groups

    @staticmethod
    def get_user_groups(username):
        groups = []
        ret = IPBoardManager.exec_xmlrpc('getUserGroups', username=username)
        if type(ret) is list:
            for group in ret:
                groups.append(group["g_title"])
        logger.debug("Got user %s IPBoard groups %s" % (username, groups))
        return groups

    @staticmethod
    def add_group(group):
        ret = IPBoardManager.exec_xmlrpc('addGroup', group=group)
        logger.info("Added IPBoard group %s" % group)
        return ret

    @staticmethod
    def add_user_to_group(username, group):
        ret = IPBoardManager.exec_xmlrpc('addUserToGroup', username=username, group=group)
        logger.info("Added IPBoard user %s to group %s" % (username, group))
        return ret

    @staticmethod
    def remove_user_from_group(username, group):
        ret = IPBoardManager.exec_xmlrpc('removeUserFromGroup', username=username, group=group)
        logger.info("Removed IPBoard user %s from group %s" % (username, group))
        return ret

    @staticmethod
    def help_me():
        ret = IPBoardManager.exec_xmlrpc('helpMe')
        return ret

    @staticmethod
    def update_groups(username, groups):
        logger.debug("Updating IPBoard user %s with groups %s" % (username, groups))
        forum_groups = IPBoardManager.get_all_groups()
        user_groups = set(IPBoardManager.get_user_groups(username))
        act_groups = set([IPBoardManager._sanitize_groupname(g) for g in groups])
        addgroups = act_groups - user_groups
        remgroups = user_groups - act_groups

        logger.info("Updating IPBoard groups for user %s - adding %s, removing %s" % (username, addgroups, remgroups))
        for g in addgroups:
            if g not in forum_groups:
                IPBoardManager.add_group(g)
            logger.debug("Adding user %s to IPBoard group %s" % (username, g))
            IPBoardManager.add_user_to_group(username, g)

        for g in remgroups:
            logger.debug("Removing user %s from IPBoard group %s" % (username, g))
            IPBoardManager.remove_user_from_group(username, g)

    @staticmethod
    def update_user_password(username, email, plain_password=None):
        logger.debug("Settings new IPBoard password for user %s" % username)
        if not plain_password:
            plain_password = IPBoardManager.__generate_random_pass()
        IPBoardManager.update_user(username, email, plain_password)
        return plain_password
