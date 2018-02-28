import random
import string
import calendar
from datetime import datetime
import hashlib
import logging
import re

from django.db import connections
from django.conf import settings

logger = logging.getLogger(__name__)


TABLE_PREFIX = getattr(settings, 'SMF_TABLE_PREFIX', 'smf_')


class SmfManager:
    def __init__(self):
        pass

    SQL_ADD_USER = r"INSERT INTO %smembers (member_name, passwd, email_address, date_registered, real_name," \
                   r" buddy_list, message_labels, openid_uri, signature, ignore_boards) " \
                   r"VALUES (%%s, %%s, %%s, %%s, %%s, 0, 0, 0, 0, 0)" % TABLE_PREFIX

    SQL_DEL_USER = r"DELETE FROM %smembers where member_name = %%s" % TABLE_PREFIX

    SQL_DIS_USER = r"UPDATE %smembers SET email_address = %%s, passwd = %%s WHERE member_name = %%s" % TABLE_PREFIX

    SQL_USER_ID_FROM_USERNAME = r"SELECT id_member from %smembers WHERE member_name = %%s" % TABLE_PREFIX

    SQL_ADD_USER_GROUP = r"UPDATE %smembers SET additional_groups = %%s WHERE id_member = %%s" % TABLE_PREFIX

    SQL_GET_GROUP_ID = r"SELECT id_group from %smembergroups WHERE group_name = %%s" % TABLE_PREFIX

    SQL_ADD_GROUP = r"INSERT INTO %smembergroups (group_name,description) VALUES (%%s,%%s)" % TABLE_PREFIX

    SQL_UPDATE_USER_PASSWORD = r"UPDATE %smembers SET passwd = %%s WHERE member_name = %%s" % TABLE_PREFIX

    SQL_REMOVE_USER_GROUP = r"UPDATE %smembers SET additional_groups = %%s WHERE id_member = %%s" % TABLE_PREFIX

    SQL_GET_ALL_GROUPS = r"SELECT id_group, group_name FROM %smembergroups" % TABLE_PREFIX

    SQL_GET_USER_GROUPS = r"SELECT additional_groups FROM %smembers WHERE id_member = %%s" % TABLE_PREFIX

    SQL_ADD_USER_AVATAR = r"UPDATE %smembers SET avatar = %%s WHERE id_member = %%s" % TABLE_PREFIX

    @staticmethod
    def _sanitize_groupname(name):
        name = name.strip(' _')
        return re.sub('[^\w.-]', '', name)

    @staticmethod
    def generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def gen_hash(username_clean, passwd):
        return hashlib.sha1((username_clean + passwd).encode('utf-8')).hexdigest()

    @staticmethod
    def santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "_")
        return sanatized.lower()

    @staticmethod
    def get_current_utc_date():
        d = datetime.utcnow()
        unixtime = calendar.timegm(d.utctimetuple())
        return unixtime

    @classmethod
    def create_group(cls, groupname):
        logger.debug("Creating smf group %s" % groupname)
        cursor = connections['smf'].cursor()
        cursor.execute(cls.SQL_ADD_GROUP, [groupname, groupname])
        logger.info("Created smf group %s" % groupname)
        return cls.get_group_id(groupname)

    @classmethod
    def get_group_id(cls, groupname):
        logger.debug("Getting smf group id for groupname %s" % groupname)
        cursor = connections['smf'].cursor()
        cursor.execute(cls.SQL_GET_GROUP_ID, [groupname])
        row = cursor.fetchone()
        logger.debug("Got smf group id %s for groupname %s" % (row[0], groupname))
        return row[0]

    @classmethod
    def check_user(cls, username):
        logger.debug("Checking smf username %s" % username)
        cursor = connections['smf'].cursor()
        cursor.execute(cls.SQL_USER_ID_FROM_USERNAME, [cls.santatize_username(username)])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s on smf" % username)
            return True
        logger.debug("User %s not found on smf" % username)
        return False

    @classmethod
    def add_avatar(cls, member_name, characterid):
        logger.debug("Adding EVE character id %s portrait as smf avatar for user %s" % (characterid, member_name))
        avatar_url = "https://image.eveonline.com/Character/" + characterid + "_64.jpg"
        cursor = connections['smf'].cursor()
        id_member = cls.get_user_id(member_name)
        cursor.execute(cls.SQL_ADD_USER_AVATAR, [avatar_url, id_member])

    @classmethod
    def get_user_id(cls, username):
        logger.debug("Getting smf user id for username %s" % username)
        cursor = connections['smf'].cursor()
        cursor.execute(cls.SQL_USER_ID_FROM_USERNAME, [username])
        row = cursor.fetchone()
        if row is not None:
            logger.debug("Got smf user id %s for username %s" % (row[0], username))
            return row[0]
        else:
            logger.error("username %s not found on smf. Unable to determine user id ." % username)
            return None

    @classmethod
    def get_all_groups(cls):
        logger.debug("Getting all smf groups.")
        cursor = connections['smf'].cursor()
        cursor.execute(cls.SQL_GET_ALL_GROUPS)
        rows = cursor.fetchall()
        out = {}
        for row in rows:
            out[row[1]] = row[0]
        logger.debug("Got smf groups %s" % out)
        return out

    @classmethod
    def get_user_groups(cls, userid):
        logger.debug("Getting smf user id %s groups" % userid)
        cursor = connections['smf'].cursor()
        cursor.execute(cls.SQL_GET_USER_GROUPS, [userid])
        out = [row[0] for row in cursor.fetchall()]
        logger.debug("Got user %s smf groups %s" % (userid, out))
        return out

    @classmethod
    def add_user(cls, username, email_address, groups, characterid):
        logger.debug("Adding smf user with member_name %s, email_address %s, characterid %s" % (
            username, email_address, characterid))
        cursor = connections['smf'].cursor()
        username_clean = cls.santatize_username(username)
        passwd = cls.generate_random_pass()
        pwhash = cls.gen_hash(username_clean, passwd)
        logger.debug("Proceeding to add smf user %s and pwhash starting with %s" % (username, pwhash[0:5]))
        register_date = cls.get_current_utc_date()
        # check if the username was simply revoked
        if cls.check_user(username) is True:
            logger.warn("Unable to add smf user with username %s - already exists. Updating user instead." % username)
            cls.__update_user_info(username_clean, email_address, pwhash)
        else:
            try:
                cursor.execute(cls.SQL_ADD_USER,
                               [username_clean, passwd, email_address, register_date, username_clean])
                cls.add_avatar(username_clean, characterid)
                logger.info("Added smf member_name %s" % username_clean)
                cls.update_groups(username_clean, groups)
            except:
                logger.warn("Unable to add smf user %s" % username_clean)
                pass
        return username_clean, passwd

    @classmethod
    def __update_user_info(cls, username, email_address, passwd):
        logger.debug(
            "Updating smf user %s info: username %s password of length %s" % (username, email_address, len(passwd)))
        cursor = connections['smf'].cursor()
        try:
            cursor.execute(cls.SQL_DIS_USER, [email_address, passwd, username])
            logger.info("Updated smf user %s info" % username)
        except:
            logger.exception("Unable to update smf user %s info." % username)
            pass

    @classmethod
    def delete_user(cls, username):
        logger.debug("Deleting smf user %s" % username)
        cursor = connections['smf'].cursor()

        if cls.check_user(username):
            cursor.execute(cls.SQL_DEL_USER, [username])
            logger.info("Deleted smf user %s" % username)
            return True
        logger.error("Unable to delete smf user %s - user not found on smf." % username)
        return False

    @classmethod
    def update_groups(cls, username, groups):
        userid = cls.get_user_id(username)
        logger.debug("Updating smf user %s with id %s groups %s" % (username, userid, groups))
        if userid is not None:
            forum_groups = cls.get_all_groups()
            user_groups = set(cls.get_user_groups(userid))
            act_groups = set([cls._sanitize_groupname(g) for g in groups])
            addgroups = act_groups - user_groups
            remgroups = user_groups - act_groups
            logger.info("Updating smf user %s groups - adding %s, removing %s" % (username, addgroups, remgroups))
            act_group_id = set()
            for g in addgroups:
                if g not in forum_groups:
                    forum_groups[g] = cls.create_group(g)
                act_group_id.add(str(cls.get_group_id(g)))
            string_groups = ','.join(act_group_id)
            cls.add_user_to_group(userid, string_groups)

    @classmethod
    def add_user_to_group(cls, userid, groupid):
        logger.debug("Adding smf user id %s to group id %s" % (userid, groupid))
        try:
            cursor = connections['smf'].cursor()
            cursor.execute(cls.SQL_ADD_USER_GROUP, [groupid, userid])
            logger.info("Added smf user id %s to group id %s" % (userid, groupid))
        except:
            logger.exception("Unable to add smf user id %s to group id %s" % (userid, groupid))
            pass

    @classmethod
    def remove_user_from_group(cls, userid, groupid):
        logger.debug("Removing smf user id %s from group id %s" % (userid, groupid))
        try:
            cursor = connections['smf'].cursor()
            cursor.execute(cls.SQL_REMOVE_USER_GROUP, [groupid, userid])
            logger.info("Removed smf user id %s from group id %s" % (userid, groupid))
        except:
            logger.exception("Unable to remove smf user id %s from group id %s" % (userid, groupid))
            pass

    @classmethod
    def disable_user(cls, username):
        logger.debug("Disabling smf user %s" % username)
        cursor = connections['smf'].cursor()

        password = cls.generate_random_pass()
        revoke_email = "revoked@localhost"
        try:
            pwhash = cls.gen_hash(username, password)
            cursor.execute(cls.SQL_DIS_USER, [revoke_email, pwhash, username])
            cls.get_user_id(username)
            cls.update_groups(username, [])
            logger.info("Disabled smf user %s" % username)
            return True
        except TypeError:
            logger.exception("TypeError occured while disabling user %s - failed to disable." % username)
            return False

    @classmethod
    def update_user_password(cls, username, characterid, password=None):
        logger.debug("Updating smf user %s password" % username)
        cursor = connections['smf'].cursor()
        if not password:
            password = cls.generate_random_pass()
        if cls.check_user(username):
            username_clean = cls.santatize_username(username)
            pwhash = cls.gen_hash(username_clean, password)
            logger.debug(
                "Proceeding to update smf user %s password with pwhash starting with %s" % (username, pwhash[0:5]))
            cursor.execute(cls.SQL_UPDATE_USER_PASSWORD, [pwhash, username])
            cls.add_avatar(username, characterid)
            logger.info("Updated smf user %s password." % username)
            return password
        logger.error("Unable to update smf user %s password - user not found on smf." % username)
        return ""
