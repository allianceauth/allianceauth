import random
import string
import calendar
import re
from datetime import datetime

from passlib.apps import phpbb3_context
from django.db import connections

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


TABLE_PREFIX = getattr(settings, 'PHPBB3_TABLE_PREFIX', 'phpbb_')


class Phpbb3Manager:
    SQL_ADD_USER = r"INSERT INTO %susers (username, username_clean, " \
                   r"user_password, user_email, group_id, user_regdate, user_permissions, " \
                   r"user_sig, user_lang) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, 'en')" % TABLE_PREFIX

    SQL_DEL_USER = r"DELETE FROM %susers where username = %%s" % TABLE_PREFIX

    SQL_DIS_USER = r"UPDATE %susers SET user_email= %%s, user_password=%%s WHERE username = %%s" % TABLE_PREFIX

    SQL_USER_ID_FROM_USERNAME = r"SELECT user_id from %susers WHERE username = %%s" % TABLE_PREFIX

    SQL_ADD_USER_GROUP = r"INSERT INTO %suser_group (group_id, user_id, user_pending) VALUES (%%s, %%s, %%s)" % TABLE_PREFIX

    SQL_GET_GROUP_ID = r"SELECT group_id from %sgroups WHERE group_name = %%s" % TABLE_PREFIX

    SQL_ADD_GROUP = r"INSERT INTO %sgroups (group_name,group_desc,group_legend) VALUES (%%s,%%s,0)" % TABLE_PREFIX

    SQL_UPDATE_USER_PASSWORD = r"UPDATE %susers SET user_password = %%s WHERE username = %%s" % TABLE_PREFIX

    SQL_REMOVE_USER_GROUP = r"DELETE FROM %suser_group WHERE user_id=%%s AND group_id=%%s " % TABLE_PREFIX

    SQL_GET_ALL_GROUPS = r"SELECT group_id, group_name FROM %sgroups" % TABLE_PREFIX

    SQL_GET_USER_GROUPS = r"SELECT %(prefix)sgroups.group_name FROM %(prefix)sgroups , %(prefix)suser_group WHERE " \
                          r"%(prefix)suser_group.group_id = %(prefix)sgroups.group_id AND user_id=%%s" % {'prefix': TABLE_PREFIX}

    SQL_ADD_USER_AVATAR = r"UPDATE %susers SET user_avatar_type=2, user_avatar_width=64, user_avatar_height=64, " \
                          "user_avatar=%%s WHERE user_id = %%s" % TABLE_PREFIX

    SQL_CLEAR_USER_PERMISSIONS = r"UPDATE %susers SET user_permissions = '' WHERE user_id = %%s" % TABLE_PREFIX

    SQL_DEL_SESSION = r"DELETE FROM %ssessions where session_user_id = %%s" % TABLE_PREFIX

    SQL_DEL_AUTOLOGIN = r"DELETE FROM %ssessions_keys where user_id = %%s" % TABLE_PREFIX

    def __init__(self):
        pass

    @staticmethod
    def __add_avatar(username, characterid):
        logger.debug("Adding EVE character id %s portrait as phpbb avater for user %s" % (characterid, username))
        avatar_url = "https://image.eveonline.com/Character/" + characterid + "_64.jpg"
        cursor = connections['phpbb3'].cursor()
        userid = Phpbb3Manager.__get_user_id(username)
        cursor.execute(Phpbb3Manager.SQL_ADD_USER_AVATAR, [avatar_url, userid])

    @staticmethod
    def __generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def __gen_hash(password):
        return phpbb3_context.encrypt(password)

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "_")
        return sanatized.lower()

    @staticmethod
    def _sanitize_groupname(name):
        name = name.strip(' _')
        return re.sub('[^\w.-]', '', name)

    @staticmethod
    def __get_group_id(groupname):
        logger.debug("Getting phpbb3 group id for groupname %s" % groupname)
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_GET_GROUP_ID, [groupname])
        row = cursor.fetchone()
        logger.debug("Got phpbb group id %s for groupname %s" % (row[0], groupname))
        return row[0]

    @staticmethod
    def __get_user_id(username):
        logger.debug("Getting phpbb3 user id for username %s" % username)
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_USER_ID_FROM_USERNAME, [username])
        row = cursor.fetchone()
        if row is not None:
            logger.debug("Got phpbb user id %s for username %s" % (row[0], username))
            return row[0]
        else:
            logger.error("Username %s not found on phpbb. Unable to determine user id." % username)
            return None

    @staticmethod
    def __get_all_groups():
        logger.debug("Getting all phpbb3 groups.")
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_GET_ALL_GROUPS)
        rows = cursor.fetchall()
        out = {}
        for row in rows:
            out[row[1]] = row[0]
        logger.debug("Got phpbb groups %s" % out)
        return out

    @staticmethod
    def __get_user_groups(userid):
        logger.debug("Getting phpbb3 user id %s groups" % userid)
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_GET_USER_GROUPS, [userid])
        out = [row[0] for row in cursor.fetchall()]
        logger.debug("Got user %s phpbb groups %s" % (userid, out))
        return out

    @staticmethod
    def __get_current_utc_date():
        d = datetime.utcnow()
        unixtime = calendar.timegm(d.utctimetuple())
        return unixtime

    @staticmethod
    def __create_group(groupname):
        logger.debug("Creating phpbb3 group %s" % groupname)
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_ADD_GROUP, [groupname, groupname])
        logger.info("Created phpbb group %s" % groupname)
        return Phpbb3Manager.__get_group_id(groupname)

    @staticmethod
    def __add_user_to_group(userid, groupid):
        logger.debug("Adding phpbb3 user id %s to group id %s" % (userid, groupid))
        try:
            cursor = connections['phpbb3'].cursor()
            cursor.execute(Phpbb3Manager.SQL_ADD_USER_GROUP, [groupid, userid, 0])
            cursor.execute(Phpbb3Manager.SQL_CLEAR_USER_PERMISSIONS, [userid])
            logger.info("Added phpbb user id %s to group id %s" % (userid, groupid))
        except:
            logger.exception("Unable to add phpbb user id %s to group id %s" % (userid, groupid))
            pass

    @staticmethod
    def __remove_user_from_group(userid, groupid):
        logger.debug("Removing phpbb3 user id %s from group id %s" % (userid, groupid))
        try:
            cursor = connections['phpbb3'].cursor()
            cursor.execute(Phpbb3Manager.SQL_REMOVE_USER_GROUP, [userid, groupid])
            cursor.execute(Phpbb3Manager.SQL_CLEAR_USER_PERMISSIONS, [userid])
            logger.info("Removed phpbb user id %s from group id %s" % (userid, groupid))
        except:
            logger.exception("Unable to remove phpbb user id %s from group id %s" % (userid, groupid))
            pass

    @staticmethod
    def add_user(username, email, groups, characterid):
        logger.debug("Adding phpbb user with username %s, email %s, groups %s, characterid %s" % (
            username, email, groups, characterid))
        cursor = connections['phpbb3'].cursor()

        username_clean = Phpbb3Manager.__santatize_username(username)
        password = Phpbb3Manager.__generate_random_pass()
        pwhash = Phpbb3Manager.__gen_hash(password)
        logger.debug("Proceeding to add phpbb user %s and pwhash starting with %s" % (username_clean, pwhash[0:5]))
        # check if the username was simply revoked
        if Phpbb3Manager.check_user(username_clean):
            logger.warn("Unable to add phpbb user with username %s - already exists. Updating user instead." % username)
            Phpbb3Manager.__update_user_info(username_clean, email, pwhash)
        else:
            try:

                cursor.execute(Phpbb3Manager.SQL_ADD_USER, [username_clean, username_clean, pwhash,
                                                            email, 2, Phpbb3Manager.__get_current_utc_date(),
                                                            "", ""])
                Phpbb3Manager.update_groups(username_clean, groups)
                Phpbb3Manager.__add_avatar(username_clean, characterid)
                logger.info("Added phpbb user %s" % username_clean)
            except:
                logger.exception("Unable to add phpbb user %s" % username_clean)
                pass

        return username_clean, password

    @staticmethod
    def disable_user(username):
        logger.debug("Disabling phpbb user %s" % username)
        cursor = connections['phpbb3'].cursor()

        password = Phpbb3Manager.__gen_hash(Phpbb3Manager.__generate_random_pass())
        revoke_email = "revoked@localhost"
        try:
            pwhash = Phpbb3Manager.__gen_hash(password)
            cursor.execute(Phpbb3Manager.SQL_DIS_USER, [revoke_email, pwhash, username])
            userid = Phpbb3Manager.__get_user_id(username)
            cursor.execute(Phpbb3Manager.SQL_DEL_AUTOLOGIN, [userid])
            cursor.execute(Phpbb3Manager.SQL_DEL_SESSION, [userid])
            Phpbb3Manager.update_groups(username, [])
            logger.info("Disabled phpbb user %s" % username)
            return True
        except TypeError:
            logger.exception("TypeError occured while disabling user %s - failed to disable." % username)
            return False

    @staticmethod
    def delete_user(username):
        logger.debug("Deleting phpbb user %s" % username)
        cursor = connections['phpbb3'].cursor()

        if Phpbb3Manager.check_user(username):
            cursor.execute(Phpbb3Manager.SQL_DEL_USER, [username])
            logger.info("Deleted phpbb user %s" % username)
            return True
        logger.error("Unable to delete phpbb user %s - user not found on phpbb." % username)
        return False

    @staticmethod
    def update_groups(username, groups):
        userid = Phpbb3Manager.__get_user_id(username)
        logger.debug("Updating phpbb user %s with id %s groups %s" % (username, userid, groups))
        if userid is not None:
            forum_groups = Phpbb3Manager.__get_all_groups()
            user_groups = set(Phpbb3Manager.__get_user_groups(userid))
            act_groups = set([Phpbb3Manager._sanitize_groupname(g) for g in groups])
            addgroups = act_groups - user_groups
            remgroups = user_groups - act_groups
            logger.info("Updating phpbb user %s groups - adding %s, removing %s" % (username, addgroups, remgroups))
            for g in addgroups:
                if not g in forum_groups:
                    forum_groups[g] = Phpbb3Manager.__create_group(g)
                Phpbb3Manager.__add_user_to_group(userid, forum_groups[g])

            for g in remgroups:
                Phpbb3Manager.__remove_user_from_group(userid, forum_groups[g])

    @staticmethod
    def remove_group(username, group):
        logger.debug("Removing phpbb user %s from group %s" % (username, group))
        cursor = connections['phpbb3'].cursor()
        userid = Phpbb3Manager.__get_user_id(username)
        if userid is not None:
            groupid = Phpbb3Manager.__get_group_id(group)

            if userid:
                if groupid:
                    try:
                        cursor.execute(Phpbb3Manager.SQL_REMOVE_USER_GROUP, [userid, groupid])
                        logger.info("Removed phpbb user %s from group %s" % (username, group))
                    except:
                        logger.exception(
                            "Exception prevented removal of phpbb user %s with id %s from group %s with id %s" % (
                                username, userid, group, groupid))
                        pass

    @staticmethod
    def check_user(username):
        logger.debug("Checking phpbb username %s" % username)
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_USER_ID_FROM_USERNAME, [Phpbb3Manager.__santatize_username(username)])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s on phpbb" % username)
            return True
        logger.debug("User %s not found on phpbb" % username)
        return False

    @staticmethod
    def update_user_password(username, characterid, password=None):
        logger.debug("Updating phpbb user %s password" % username)
        cursor = connections['phpbb3'].cursor()
        if not password:
            password = Phpbb3Manager.__generate_random_pass()
        if Phpbb3Manager.check_user(username):
            pwhash = Phpbb3Manager.__gen_hash(password)
            logger.debug(
                "Proceeding to update phpbb user %s password with pwhash starting with %s" % (username, pwhash[0:5]))
            cursor.execute(Phpbb3Manager.SQL_UPDATE_USER_PASSWORD, [pwhash, username])
            Phpbb3Manager.__add_avatar(username, characterid)
            logger.info("Updated phpbb user %s password." % username)
            return password
        logger.error("Unable to update phpbb user %s password - user not found on phpbb." % username)
        return ""

    @staticmethod
    def __update_user_info(username, email, password):
        logger.debug(
            "Updating phpbb user %s info: username %s password of length %s" % (username, email, len(password)))
        cursor = connections['phpbb3'].cursor()
        try:
            cursor.execute(Phpbb3Manager.SQL_DIS_USER, [email, password, username])
            logger.info("Updated phpbb user %s info" % username)
        except:
            logger.exception("Unable to update phpbb user %s info." % username)
            pass
