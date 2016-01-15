import os
import hashlib
import sys

import django
from django.db import connections
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

class MumbleManager:
    SQL_SELECT_USER_MAX_ID = r"SELECT max(user_id)+1 as next_id from murmur_users"

    SQL_SELECT_GROUP_MAX_ID = r"SELECT MAX(group_id)+1 FROM murmur_groups"

    SQL_CREATE_USER = r"INSERT INTO murmur_users (server_id, user_id, name, pw) VALUES (%s, %s, %s, %s)"

    SQL_SELECT_GET_USER_ID_BY_NAME = r"SELECT user_id from murmur_users WHERE name = %s AND server_id = %s"

    SQL_CHECK_USER_EXIST = r"SELECT name from murmur_users WHERE name = %s AND server_id = %s"

    SQL_DELETE_USER = r"DELETE FROM murmur_users WHERE name = %s AND server_id = %s"

    SQL_UPDATE_USER_PASSWORD = r"UPDATE murmur_users SET pw = %s WHERE name = %s AND server_id = %s"

    SQL_GET_GROUPS = r"SELECT group_id, name FROM murmur_groups WHERE server_id = %s AND channel_id = 0"

    SQL_GET_GROUP_FROM_NAME = r"SELECT group_id, name FROM murmur_groups " \
                              r"WHERE server_id = %s AND channel_id = 0 AND name = %s"

    SQL_GET_USER_GROUPS = r"SELECT murmur_groups.name FROM murmur_groups, murmur_group_members WHERE " \
                          r"murmur_group_members.group_id = murmur_groups.group_id AND " \
                          r"murmur_group_members.server_id = murmur_groups.server_id AND " \
                          r"murmur_group_members.user_id = %s"

    SQL_ADD_GROUP = r"INSERT INTO murmur_groups (group_id, server_id, name, channel_id, inherit, inheritable) " \
                    r"VALUES (%s, %s, %s, 0, 1, 1)"

    SQL_ADD_USER_TO_GROUP = r"INSERT INTO murmur_group_members (group_id, server_id, user_id, addit) " \
                            r"VALUES (%s, %s, %s, 1)"

    SQL_DELETE_USER_FROM_GROUP = r"DELETE FROM murmur_group_members WHERE group_id = %s " \
                                 r"AND server_id = %s AND user_id = %s"

    def __init__(self):
        pass

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "")
        return sanatized

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def __generate_username(username, corp_ticker):
        return "[" + corp_ticker + "]" + username

    @staticmethod
    def __generate_username_blue(username, corp_ticker):
        return "[BLUE][" + corp_ticker + "]" + username

    @staticmethod
    def _gen_pwhash(password):
        return hashlib.sha1(password).hexdigest()

    @staticmethod
    def _get_groups():
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_GET_GROUPS, [settings.MUMBLE_SERVER_ID])
        rows = dbcursor.fetchall()

        out = {}
        for row in rows:
            out[row[1]] = row[0]

        logger.debug("Got mumble groups %s" % out)
        return out

    @staticmethod
    def _get_group(name):
        logger.debug("Looking for group name %s in mumble." % name)
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_GET_GROUP_FROM_NAME, [settings.MUMBLE_SERVER_ID, name])
        row = dbcursor.fetchone()
        if row:
            logger.debug("Found group %s in mumble - %s" % (name, row[0]))
            return row[0]

    @staticmethod
    def _get_user_groups(name):
        logger.debug("Getting mumble groups for username %s" % name)
        dbcursor = connections['mumble'].cursor()
        user_id = MumbleManager.get_user_id_by_name(name)
        dbcursor.execute(MumbleManager.SQL_GET_USER_GROUPS, [user_id])
        out = [row[0] for row in dbcursor.fetchall()]
        logger.debug("Got user %s mumble groups %s" % (name, out))
        return out

    @staticmethod
    def _add_group(name):
        logger.debug("Adding group %s to mumble server." % name)
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_SELECT_GROUP_MAX_ID)
        row = dbcursor.fetchone()
        groupid = row[0]
        dbcursor.execute(MumbleManager.SQL_ADD_GROUP, [groupid, settings.MUMBLE_SERVER_ID, name])
        logger.info("Created group %s on mumble server with id %s" % (name, groupid))
        return groupid

    @staticmethod
    def _add_user_to_group(userid, groupid):
        if userid != None:
            dbcursor = connections['mumble'].cursor()
            dbcursor.execute(MumbleManager.SQL_ADD_USER_TO_GROUP, [groupid, settings.MUMBLE_SERVER_ID, userid])
            logger.info("Added user id %s to mumble group id %s" % (userid, groupid))

    @staticmethod
    def _del_user_from_group(userid, groupid):
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_DELETE_USER_FROM_GROUP, [groupid, settings.MUMBLE_SERVER_ID, userid])
        logger.info("Removed user id %s from mumble group id %s" % (userid, groupid))

    @staticmethod
    def get_user_id_by_name(name):
        logger.debug("Getting mumble user id for user with name %s" % name)
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_SELECT_GET_USER_ID_BY_NAME, [name, settings.MUMBLE_SERVER_ID])
        row = dbcursor.fetchone()
        if row:
            logger.debug("Got mumble user id %s for name %s" % (row[0], name))
            return row[0]

    @staticmethod
    def create_user(corp_ticker, username):
        logger.debug("Creating mumble user with username %s and ticker %s" % (username, corp_ticker))
        dbcursor = connections['mumble'].cursor()
        username_clean = MumbleManager.__santatize_username(MumbleManager.__generate_username(username, corp_ticker))
        password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user creation: clean username %s, pwhash starts with %s" % (username_clean, pwhash[0:5]))
        try:
            dbcursor.execute(MumbleManager.SQL_SELECT_USER_MAX_ID)
            user_id = dbcursor.fetchone()[0]

            dbcursor.execute(MumbleManager.SQL_CREATE_USER,
                             [settings.MUMBLE_SERVER_ID, user_id, username_clean, pwhash])
            logger.info("Added user to mumble with username %s" % username_clean)
            return username_clean, password
        except django.db.utils.IntegrityError as error:
            logger.exception("IntegrityError during mumble create_user occured.", exc_info=True)
        except:
            logger.exception("Unhandled exception occured.", exc_info=True)
        logger.error("Exception prevented creation of mumble user. Returning blank for username, password.")
        return "", ""

    @staticmethod
    def create_blue_user(corp_ticker, username):
        logger.debug("Creating mumble blue user with username %s and ticker %s" % (username, corp_ticker))
        dbcursor = connections['mumble'].cursor()
        username_clean = MumbleManager.__santatize_username(MumbleManager.__generate_username_blue(username,
                                                                corp_ticker))
        password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user creation: clean username %s, pwhash starts with %s" % (username_clean, pwhash[0:5]))
        try:
            dbcursor.execute(MumbleManager.SQL_SELECT_USER_MAX_ID)
            user_id = dbcursor.fetchone()[0]

            dbcursor.execute(MumbleManager.SQL_CREATE_USER,
                             [settings.MUMBLE_SERVER_ID, user_id, username_clean, pwhash])
            logger.info("Added blue user to mumble with username %s" % username_clean)
            return username_clean, password
        except:
            logger.exception("Unhandled exception occured.", exc_info=True)
        logger.error("Exception prevented creation of mumble blue user. Returning blank for username, password.")
        return "", ""

    @staticmethod
    def check_user_exist(username):
        logger.debug("Checking if username %s exists on mumble." % username)
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_CHECK_USER_EXIST,
                         [username, settings.MUMBLE_SERVER_ID])

        row = dbcursor.fetchone()
        if row and row[0].lower() == username.lower():
            logger.debug("Found username %s on mumble." % username)
            return True
        logger.debug("Unable to find username %s on mumble." % username)
        return False

    @staticmethod
    def delete_user(username):
        logger.debug("Deleting user %s from mumble." % username)
        dbcursor = connections['mumble'].cursor()
        if MumbleManager.check_user_exist(username):
            try:

                dbcursor.execute(MumbleManager.SQL_DELETE_USER,
                                 [username, settings.MUMBLE_SERVER_ID])
                logger.info("Deleted user %s from mumble." % username)
                return True
            except:
                logger.exception("Exception prevented deletion of user %s from mumble." % username, exc_info=True)
                return False
        logger.error("User %s not found on mumble. Unable to delete." % username)
        return False

    @staticmethod
    def update_user_password(username, password=None):
        logger.debug("Updating mumble user %s password." % username)
        dbcursor = connections['mumble'].cursor()
        if not password:
            password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user %s password update - pwhash starts with %s" % (username, pwhash[0:5]))
        if MumbleManager.check_user_exist(username):
            try:

                dbcursor.execute(MumbleManager.SQL_UPDATE_USER_PASSWORD,
                                 [pwhash, username, settings.MUMBLE_SERVER_ID])
                logger.info("Updated mumble user %s password." % username)
                return password
            except:
                logger.exception("Exception prevented updating of mumble user %s password." % username, exc_info=True)
                return ""
        logger.error("User %s not found on mumble. Unable to update password." % username)
        return ""

    @staticmethod
    def update_groups(username, groups):
        logger.debug("Updating mumble user %s groups %s" % (username, groups))
        userid = MumbleManager.get_user_id_by_name(username)
        mumble_groups = MumbleManager._get_groups()
        user_groups = set(MumbleManager._get_user_groups(username))
        act_groups = set([g.replace(' ', '-') for g in groups])
        addgroups = act_groups - user_groups
        remgroups = user_groups - act_groups
        logger.info("Updating mumble user %s groups - adding %s, removing %s" % (username, addgroups, remgroups))
        for g in addgroups:
            if not g in mumble_groups:
                mumble_groups[g] = MumbleManager._add_group(g)
            try:
                logger.debug("Adding mumble user %s to group %s" % (userid, mumble_groups[g]))
                MumbleManager._add_user_to_group(userid, mumble_groups[g])
            except:
                logger.exception("Exception occured while adding mumble user %s with id %s to group %s with id %s" % (username, userid, g, mumble_groups[g]), exc_info=True)

        for g in remgroups:
            try:
                logger.debug("Deleting mumble user %s from group %s" % (userid, mumble_groups[g]))
                MumbleManager._del_user_from_group(userid, mumble_groups[g])
            except:
                logger.exception("Exception occured while removing mumble user %s with id %s from group %s with id %s" % (username, userid, g, mumble_groups[g]), exc_info=True)
