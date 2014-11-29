import os
import xmlrpclib
from hashlib import md5

from django.conf import settings


class IPBoardManager:
    def __init__(self):
        pass

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def exec_xmlrpc(func, **kwargs):
        """ Send a XMLRPC request """
        try:
            server = xmlrpclib.Server(settings.IPBOARD_ENDPOINT, verbose=False)
            params = {}
            for i in kwargs:
                params[i] = kwargs[i]
            params['api_key'] = settings.IPBOARD_APIKEY
            params['api_module'] = settings.IPBOARD_APIMODULE
            print params

            return getattr(server, func)(params)
        except:
            return {}

    @staticmethod
    def add_user(username, email):
        """ Add user to service """
        sanatized = str(IPBoardManager.__santatize_username(username))
        plain_password = IPBoardManager.__generate_random_pass()
        password = md5(plain_password).hexdigest()
        ret = IPBoardManager.exec_xmlrpc('createUser', username=sanatized, email=str(email), display_name=sanatized,
                                         md5_passwordHash=password)
        return sanatized, plain_password

    @staticmethod
    def delete_user(username):
        """ Delete user """
        ret = IPBoardManager.exec_xmlrpc('deleteUser', username=username)
        return username

    @staticmethod
    def disable_user(username):
        """ Disable user """
        ret = IPBoardManager.exec_xmlrpc('disableUser', username=username)
        return username

    @staticmethod
    def update_user(username, email, password):
        """ Add user to service """
        password = md5(password).hexdigest()
        ret = IPBoardManager.exec_xmlrpc('updateUser', username=username, email=email, md5_passwordHash=password)
        return username

    @staticmethod
    def get_all_groups():
        groups = []
        ret = IPBoardManager.exec_xmlrpc('getAllGroups')
        for group in ret:
            groups.append(group["g_title"])
        return groups

    @staticmethod
    def get_user_groups(username):
        groups = []
        ret = IPBoardManager.exec_xmlrpc('getUserGroups', username=username)
        if type(ret) is list:
            for group in ret:
                groups.append(group["g_title"])
        return groups

    @staticmethod
    def add_group(group):
        ret = IPBoardManager.exec_xmlrpc('addGroup', group=group)
        return ret

    @staticmethod
    def add_user_to_group(username, group):
        ret = IPBoardManager.exec_xmlrpc('addUserToGroup', username=username, group=group)
        return ret

    @staticmethod
    def remove_user_from_group(username, group):
        ret = IPBoardManager.exec_xmlrpc('removeUserFromGroup', username=username, group=group)
        return ret

    @staticmethod
    def help_me():
        "Random help me"
        ret = IPBoardManager.exec_xmlrpc('helpMe')
        return ret

    @staticmethod
    def update_groups(username, groups):

        forum_groups = IPBoardManager.get_all_groups()
        user_groups = set(IPBoardManager.get_user_groups(username))
        act_groups = set([g.replace(' ', '-') for g in groups])
        addgroups = act_groups - user_groups
        remgroups = user_groups - act_groups

        print addgroups
        print remgroups
        for g in addgroups:
            if not g in forum_groups:
                IPBoardManager.add_group(g)
            print username
            print g
            IPBoardManager.add_user_to_group(username, g)

        for g in remgroups:
            IPBoardManager.remove_user_from_group(username, g)

    @staticmethod
    def update_user_password(username, email):
        plain_password = IPBoardManager.__generate_random_pass()
        IPBoardManager.update_user(username, email, plain_password)
        return plain_password