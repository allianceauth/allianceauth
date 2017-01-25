from __future__ import unicode_literals

import logging

from django.conf import settings

from services.modules.teamspeak3.util.ts3 import TS3Server, TeamspeakError
from .models import TSgroup

logger = logging.getLogger(__name__)


class Teamspeak3Manager:
    def __init__(self):
        pass

    @staticmethod
    def __get_created_server():
        server = TS3Server(settings.TEAMSPEAK3_SERVER_IP, settings.TEAMSPEAK3_SERVER_PORT)
        server.login(settings.TEAMSPEAK3_SERVERQUERY_USER, settings.TEAMSPEAK3_SERVERQUERY_PASSWORD)
        server.use(settings.TEAMSPEAK3_VIRTUAL_SERVER)
        logger.debug("Got TS3 server instance based on settings.")
        return server

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "-")
        return sanatized

    @staticmethod
    def __generate_username(username, corp_ticker):
        sanatized = "[" + corp_ticker + "]" + username
        return sanatized[:30]

    @staticmethod
    def __generate_username_blue(username, corp_ticker):
        sanatized = "[BLUE][" + corp_ticker + "]" + username
        return sanatized[:30]

    @staticmethod
    def _get_userid(uid):
        logger.debug("Looking for uid %s on TS3 server." % uid)
        server = Teamspeak3Manager.__get_created_server()
        try:
            ret = server.send_command('customsearch', {'ident': 'sso_uid', 'pattern': uid})
            if ret and 'keys' in ret and 'cldbid' in ret['keys']:
                logger.debug("Got userid %s for uid %s" % (ret['keys']['cldbid'], uid))
                return ret['keys']['cldbid']
        except TeamspeakError as e:
            if not e.code == '1281':
                raise e
        return None

    @staticmethod
    def _group_id_by_name(groupname):
        server = Teamspeak3Manager.__get_created_server()
        logger.debug("Looking for group %s on TS3 server." % groupname)
        group_cache = server.send_command('servergrouplist')
        logger.debug("Received group cache from server: %s" % group_cache)
        for group in group_cache:
            logger.debug("Checking group %s" % group)
            if group['keys']['name'] == groupname:
                logger.debug("Found group %s, returning id %s" % (groupname, group['keys']['sgid']))
                return group['keys']['sgid']
        logger.debug("Group %s not found on server." % groupname)
        return None

    @staticmethod
    def _create_group(groupname):
        logger.debug("Creating group %s on TS3 server." % groupname)
        server = Teamspeak3Manager.__get_created_server()
        sgid = Teamspeak3Manager._group_id_by_name(groupname)
        if not sgid:
            logger.debug("Group does not yet exist. Proceeding with creation.")
            ret = server.send_command('servergroupadd', {'name': groupname})
            Teamspeak3Manager.__group_cache = None
            sgid = ret['keys']['sgid']
            server.send_command('servergroupaddperm',
                                {'sgid': sgid, 'permsid': 'i_group_needed_modify_power', 'permvalue': 75,
                                 'permnegated': 0, 'permskip': 0})
            server.send_command('servergroupaddperm',
                                {'sgid': sgid, 'permsid': 'i_group_needed_member_add_power', 'permvalue': 100,
                                 'permnegated': 0, 'permskip': 0})
            server.send_command('servergroupaddperm',
                                {'sgid': sgid, 'permsid': 'i_group_needed_member_remove_power', 'permvalue': 100,
                                 'permnegated': 0, 'permskip': 0})
        logger.info("Created group on TS3 server with name %s and id %s" % (groupname, sgid))
        return sgid

    @staticmethod
    def _user_group_list(cldbid):
        logger.debug("Retrieving group list for user with id %s" % cldbid)
        server = Teamspeak3Manager.__get_created_server()
        try:
            groups = server.send_command('servergroupsbyclientid', {'cldbid': cldbid})
        except TeamspeakError as e:
            if e.code == '1281': # no groups
                groups = []
            else:
                raise e
        logger.debug("Retrieved group list: %s" % groups)
        outlist = {}

        if type(groups) == list:
            logger.debug("Recieved multiple groups. Iterating.")
            for group in groups:
                outlist[group['keys']['name']] = group['keys']['sgid']
        elif type(groups) == dict:
            logger.debug("Recieved single group.")
            outlist[groups['keys']['name']] = groups['keys']['sgid']
        logger.debug("Returning name/id pairing: %s" % outlist)
        return outlist

    @staticmethod
    def _group_list():
        logger.debug("Retrieving group list on TS3 server.")
        server = Teamspeak3Manager.__get_created_server()
        group_cache = server.send_command('servergrouplist')
        logger.debug("Received group cache from server: %s" % group_cache)
        outlist = {}
        if group_cache:
            for group in group_cache:
                logger.debug("Assigning name/id dict: %s = %s" % (group['keys']['name'], group['keys']['sgid']))
                outlist[group['keys']['name']] = group['keys']['sgid']
        else:
            logger.error("Received empty group cache while retrieving group cache from TS3 server. 1024 error.")
        logger.debug("Returning name/id pairing: %s" % outlist)
        return outlist

    @staticmethod
    def _add_user_to_group(uid, groupid):
        logger.debug("Adding group id %s to TS3 user id %s" % (groupid, uid))
        server = Teamspeak3Manager.__get_created_server()
        user_groups = Teamspeak3Manager._user_group_list(uid)

        if groupid not in user_groups.values():
            logger.debug("User does not have group already. Issuing command to add.")
            server.send_command('servergroupaddclient',
                                {'sgid': str(groupid), 'cldbid': uid})
            logger.info("Added user id %s to group id %s on TS3 server." % (uid, groupid))

    @staticmethod
    def _remove_user_from_group(uid, groupid):
        logger.debug("Removing group id %s from TS3 user id %s" % (groupid, uid))
        server = Teamspeak3Manager.__get_created_server()
        user_groups = Teamspeak3Manager._user_group_list(uid)

        if str(groupid) in user_groups.values():
            logger.debug("User is in group. Issuing command to remove.")
            server.send_command('servergroupdelclient',
                                {'sgid': str(groupid), 'cldbid': uid})
            logger.info("Removed user id %s from group id %s on TS3 server." % (uid, groupid))

    @staticmethod
    def _sync_ts_group_db():
        logger.debug("_sync_ts_group_db function called.")
        try:
            remote_groups = Teamspeak3Manager._group_list()
            local_groups = TSgroup.objects.all()
            logger.debug("Comparing remote groups to TSgroup objects: %s" % local_groups)
            for key in remote_groups:
                logger.debug("Typecasting remote_group value at position %s to int: %s" % (key, remote_groups[key]))
                remote_groups[key] = int(remote_groups[key])

            for group in local_groups:
                logger.debug("Checking local group %s" % group)
                if group.ts_group_id not in remote_groups.values():
                    logger.debug(
                        "Local group id %s not found on server. Deleting model %s" % (group.ts_group_id, group))
                    TSgroup.objects.filter(ts_group_id=group.ts_group_id).delete()
            for key in remote_groups:
                g = TSgroup(ts_group_id=remote_groups[key], ts_group_name=key)
                q = TSgroup.objects.filter(ts_group_id=g.ts_group_id)
                if not q:
                    logger.debug("Local group does not exist for TS group %s. Creating TSgroup model %s" % (
                        remote_groups[key], g))
                    g.save()
        except TeamspeakError as e:
            logger.error("Error occured while syncing TS group db: %s" % str(e))
        except:
            logger.exception("An unhandled exception has occured while syncing TS groups.")

    @staticmethod
    def add_user(username, corp_ticker):
        username_clean = Teamspeak3Manager.__santatize_username(Teamspeak3Manager.__generate_username(username,
                                                                                                      corp_ticker))
        server = Teamspeak3Manager.__get_created_server()
        logger.debug("Adding user to TS3 server with cleaned username %s" % username_clean)
        server_groups = Teamspeak3Manager._group_list()

        if settings.DEFAULT_AUTH_GROUP not in server_groups:
            Teamspeak3Manager._create_group(settings.DEFAULT_AUTH_GROUP)

        alliance_group_id = Teamspeak3Manager._group_id_by_name(settings.DEFAULT_AUTH_GROUP)

        try:
            ret = server.send_command('tokenadd', {'tokentype': 0, 'tokenid1': alliance_group_id, 'tokenid2': 0,
                                                   'tokendescription': username_clean,
                                                   'tokencustomset': "ident=sso_uid value=%s" % username_clean})
        except TeamspeakError as e:
            logger.error("Failed to add teamspeak user %s: %s" % (username, str(e)))
            return "",""

        try:
            token = ret['keys']['token']
            logger.info("Created permission token for user %s on TS3 server" % username_clean)
            return username_clean, token
        except:
            logger.exception("Failed to add teamspeak user %s - received response: %s" % (username_clean, ret))
            return "", ""

    @staticmethod
    def add_blue_user(username, corp_ticker):
        username_clean = Teamspeak3Manager.__santatize_username(Teamspeak3Manager.__generate_username_blue(username,
                                                                                                           corp_ticker))
        server = Teamspeak3Manager.__get_created_server()
        logger.debug("Adding user to TS3 server with cleaned username %s" % username_clean)
        server_groups = Teamspeak3Manager._group_list()
        if settings.DEFAULT_BLUE_GROUP not in server_groups:
            Teamspeak3Manager._create_group(settings.DEFAULT_BLUE_GROUP)

        blue_group_id = Teamspeak3Manager._group_id_by_name(settings.DEFAULT_BLUE_GROUP)

        try:
            ret = server.send_command('tokenadd', {'tokentype': 0, 'tokenid1': blue_group_id, 'tokenid2': 0,
                                                   'tokendescription': username_clean,
                                                   'tokencustomset': "ident=sso_uid value=%s" % username_clean})
        except TeamspeakError as e:
            logger.error("Failed to add blue teamspeak user %s: %s" % (username, str(e)))
            return "",""

        try:
            token = ret['keys']['token']
            logger.info("Created permission token for blue user %s on TS3 server" % username_clean)
            return username_clean, token
        except:
            logger.exception("Failed to add blue teamspeak user %s - received response: %s" % (username_clean, ret))
            return "", ""

    @staticmethod
    def delete_user(uid):
        server = Teamspeak3Manager.__get_created_server()
        user = Teamspeak3Manager._get_userid(uid)
        logger.debug("Deleting user %s with id %s from TS3 server." % (user, uid))
        if user:
            clients = server.send_command('clientlist')
            for client in clients:
                try:
                    if client['keys']['client_database_id'] == user:
                        logger.debug("Found user %s on TS3 server - issuing deletion command." % user)
                        server.send_command('clientkick', {'clid': client['keys']['clid'], 'reasonid': 5,
                                                           'reasonmsg': 'Auth service deleted'})
                except:
                    logger.exception("Failed to delete user id %s from TS3 - received response %s" % (uid, client))
                    return False
            try:
                ret = server.send_command('clientdbdelete', {'cldbid': user})
            except TeamspeakError as e:
                logger.error("Failed to delete teamspeak user %s: %s" % (uid, str(e)))
                return False
            if ret == '0':
                logger.info("Deleted user with id %s from TS3 server." % uid)
                return True
            else:
                logger.exception("Failed to delete user id %s from TS3 - received response %s" % (uid, ret))
                return False
        else:
            logger.warn("User with id %s not found on TS3 server. Assuming succesful deletion." % uid)
            return True

    @staticmethod
    def check_user_exists(uid):
        if Teamspeak3Manager._get_userid(uid):
            return True

        return False

    @staticmethod
    def generate_new_permissionkey(uid, username, corpticker):
        logger.debug("Re-issuing permission key for user id %s" % uid)
        Teamspeak3Manager.delete_user(uid)
        return Teamspeak3Manager.add_user(username, corpticker)

    @staticmethod
    def generate_new_blue_permissionkey(uid, username, corpticker):
        logger.debug("Re-issuing blue permission key for user id %s" % uid)
        Teamspeak3Manager.delete_user(uid)
        return Teamspeak3Manager.add_blue_user(username, corpticker)

    @staticmethod
    def update_groups(uid, ts_groups):
        logger.debug("Updating uid %s TS3 groups %s" % (uid, ts_groups))
        userid = Teamspeak3Manager._get_userid(uid)
        addgroups = []
        remgroups = []
        if userid is not None:
            user_ts_groups = Teamspeak3Manager._user_group_list(userid)
            logger.debug("User has groups on TS3 server: %s" % user_ts_groups)
            for key in user_ts_groups:
                user_ts_groups[key] = int(user_ts_groups[key])
            for ts_group_key in ts_groups:
                logger.debug("Checking if user has group %s on TS3 server." % ts_group_key)
                if ts_groups[ts_group_key] not in user_ts_groups.values():
                    addgroups.append(ts_groups[ts_group_key])
            for user_ts_group_key in user_ts_groups:
                if user_ts_groups[user_ts_group_key] not in ts_groups.values():
                    remgroups.append(user_ts_groups[user_ts_group_key])

            for g in addgroups:
                logger.info("Adding Teamspeak user %s into group %s" % (userid, g))
                Teamspeak3Manager._add_user_to_group(userid, g)

            for g in remgroups:
                logger.info("Removing Teamspeak user %s from group %s" % (userid, g))
                Teamspeak3Manager._remove_user_from_group(userid, g)
