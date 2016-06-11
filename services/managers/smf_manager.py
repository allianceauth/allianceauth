import os
import calendar
from datetime import datetime
import hashlib
import logging

from django.db import connections
from django.conf import settings

logger = logging.getLogger(__name__)

class smfManager:
    SQL_ADD_USER = r"INSERT INTO smf_members (member_name, passwd, email_address, date_registered, real_name," \
                   r" buddy_list, message_labels, openid_uri, signature, ignore_boards) " \
                   r"VALUES (%s, %s, %s, %s, %s, 0, 0, 0, 0, 0)"

    SQL_DEL_USER = r"DELETE FROM smf_members where member_name = %s"

    SQL_DIS_USER = r"UPDATE smf_members SET email_address = %s, passwd = %s WHERE member_name = %s"

    SQL_USER_ID_FROM_USERNAME = r"SELECT id_member from smf_members WHERE member_name = %s"

    SQL_ADD_USER_GROUP = r"UPDATE smf_members SET additional_groups = %s WHERE id_member = %s"

    SQL_GET_GROUP_ID = r"SELECT id_group from smf_membergroups WHERE group_name = %s"

    SQL_ADD_GROUP = r"INSERT INTO smf_membergroups (group_name,description) VALUES (%s,%s)"

    SQL_UPDATE_USER_PASSWORD = r"UPDATE smf_members SET passwd = %s WHERE member_name = %s"

    SQL_REMOVE_USER_GROUP = r"UPDATE smf_members SET additional_groups = %s WHERE id_member = %s"

    SQL_GET_ALL_GROUPS = r"SELECT id_group, group_name FROM smf_membergroups"

    SQL_GET_USER_GROUPS = r"SELECT additional_groups FROM smf_members WHERE id_member = %s"

    SQL_ADD_USER_AVATAR = r"UPDATE smf_members SET avatar = %s WHERE id_member = %s"



    @staticmethod
    def generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def gen_hash(username_clean, passwd):
        return hashlib.sha1((username_clean) + passwd).hexdigest()

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

    @staticmethod
    def create_group(groupname):
        logger.debug("Creating smf group %s" % groupname)
        cursor = connections['smf'].cursor()
        cursor.execute(smfManager.SQL_ADD_GROUP, [groupname, groupname])
        logger.info("Created smf group %s" % groupname)
        return smfManager.get_group_id(groupname)


    @staticmethod
    def get_group_id(groupname):
        logger.debug("Getting smf group id for groupname %s" % groupname)
        cursor = connections['smf'].cursor()
        cursor.execute(smfManager.SQL_GET_GROUP_ID, [groupname])
        row = cursor.fetchone()
        logger.debug("Got smf group id %s for groupname %s" % (row[0], groupname))
        return row[0]

    @staticmethod
    def check_user(username):
        logger.debug("Checking smf username %s" % username)
        cursor = connections['smf'].cursor()
        cursor.execute(smfManager.SQL_USER_ID_FROM_USERNAME, [smfManager.santatize_username(username)])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s on smf" % username)
            return True
        logger.debug("User %s not found on smf" % username)
        return False


    @staticmethod
    def add_avatar(member_name, characterid):
        logger.debug("Adding EVE character id %s portrait as smf avatar for user %s" % (characterid, member_name))
        avatar_url = "https://image.eveonline.com/Character/" + characterid + "_64.jpg"
        cursor = connections['smf'].cursor()
        id_member = smfManager.get_user_id(member_name)
        cursor.execute(smfManager.SQL_ADD_USER_AVATAR, [avatar_url, id_member])

    @staticmethod
    def get_user_id(username):
        logger.debug("Getting smf user id for username %s" % username)
        cursor = connections['smf'].cursor()
        cursor.execute(smfManager.SQL_USER_ID_FROM_USERNAME, [username])
        row = cursor.fetchone()
        if row is not None:
            logger.debug("Got smf user id %s for username %s" % (row[0], username))
            return row[0]
        else:
            logger.error("username %s not found on smf. Unable to determine user id ." % username)
            return None

    @staticmethod
    def get_all_groups():
        logger.debug("Getting all smf groups.")
        cursor = connections['smf'].cursor()
        cursor.execute(smfManager.SQL_GET_ALL_GROUPS)
        rows = cursor.fetchall()
        out = {}
        for row in rows:
            out[row[1]] = row[0]
        logger.debug("Got smf groups %s" % out)
        return out

    @staticmethod
    def get_user_groups(userid):
        logger.debug("Getting smf user id %s groups" % userid)
        cursor = connections['smf'].cursor()
        cursor.execute(smfManager.SQL_GET_USER_GROUPS, [userid])
        out = [row[0] for row in cursor.fetchall()]
        logger.debug("Got user %s smf groups %s" % (userid, out))
        return out

    @staticmethod
    def add_user(username, email_address, groups, characterid):
        logger.debug("Adding smf user with member_name %s, email_address %s, characterid %s" % (username, email_address, characterid))
        cursor = connections['smf'].cursor()
        username_clean = smfManager.santatize_username(username)
        passwd = smfManager.generate_random_pass()
        pwhash = smfManager.gen_hash(username_clean, passwd)
        logger.debug("Proceeding to add smf user %s and pwhash starting with %s" % (username, pwhash[0:5]))
        register_date = smfManager.get_current_utc_date()
        # check if the username was simply revoked
        if smfManager.check_user(username)is True :
            logger.warn("Unable to add smf user with username %s - already exists. Updating user instead." % username)
            smfManager.__update_user_info(username_clean, email_address, pwhash)
        else:
            try:
                cursor.execute(smfManager.SQL_ADD_USER, [username_clean, passwd, email_address, register_date, username_clean])
                smfManager.add_avatar(username_clean, characterid)
                logger.info("Added smf member_name %s" % username_clean)
                smfManager.update_groups(username_clean, groups)
            except:
                logger.warn("Unable to add smf user %s" % username_clean)
                pass
        return username_clean, passwd

    @staticmethod
    def __update_user_info(username, email_address, passwd):
        logger.debug("Updating smf user %s info: username %s password of length %s" % (username, email_address, len(passwd)))
        cursor = connections['smf'].cursor()
        try:
            cursor.execute(smfManager.SQL_DIS_USER, [email_address, passwd, username])
            logger.info("Updated smf user %s info" % username)
        except:
            logger.exception("Unable to update smf user %s info." % username)
            pass

    @staticmethod
    def delete_user(username):
        logger.debug("Deleting smf user %s" % username)
        cursor = connections['smf'].cursor()

        if smfManager.check_user(username):
            cursor.execute(smfManager.SQL_DEL_USER, [username])
            logger.info("Deleted smf user %s" % username)
            return True
        logger.error("Unable to delete smf user %s - user not found on smf." % username)
        return False

    @staticmethod
    def update_groups(username, groups):
        userid = smfManager.get_user_id(username)
        logger.debug("Updating smf user %s with id %s groups %s" % (username, userid, groups))
        if userid is not None:
            forum_groups = smfManager.get_all_groups()
            user_groups = set(smfManager.get_user_groups(userid))
            act_groups = set([g.replace(' ', '-') for g in groups])
            addgroups = act_groups - user_groups
            remgroups = user_groups - act_groups
            logger.info("Updating smf user %s groups - adding %s, removing %s" % (username, addgroups, remgroups))
            act_group_id = set()
            for g in addgroups:
                if not g in forum_groups:
                    forum_groups[g] = smfManager.create_group(g)
                act_group_id.add(str(smfManager.get_group_id(g)))
            string_groups = ','.join(act_group_id)
            smfManager.add_user_to_group(userid, string_groups)


    @staticmethod
    def add_user_to_group(userid, groupid):
        logger.debug("Adding smf user id %s to group id %s" % (userid, groupid))
        try:
            cursor = connections['smf'].cursor()
            cursor.execute(smfManager.SQL_ADD_USER_GROUP, [groupid, userid])
            logger.info("Added smf user id %s to group id %s" % (userid, groupid))
        except:
            logger.exception("Unable to add smf user id %s to group id %s" % (userid, groupid))
            pass

    @staticmethod
    def remove_user_from_group(userid, groupid):
        logger.debug("Removing smf user id %s from group id %s" % (userid, groupid))
        try:
            cursor = connections['smf'].cursor()
            cursor.execute(smfManager.SQL_REMOVE_USER_GROUP, [groupid, userid])
            logger.info("Removed smf user id %s from group id %s" % (userid, groupid))
        except:
            logger.exception("Unable to remove smf user id %s from group id %s" % (userid, groupid))
            pass

    @staticmethod
    def disable_user(username):
        logger.debug("Disabling smf user %s" % username)
        cursor = connections['smf'].cursor()

        password = smfManager.generate_random_pass()
        revoke_email = "revoked@" + settings.DOMAIN
        try:
            pwhash = smfManager.gen_hash(username, password)
            cursor.execute(smfManager.SQL_DIS_USER, [revoke_email, pwhash, username])
            userid = smfManager.get_user_id(username)
            smfManager.update_groups(username, [])
            logger.info("Disabled smf user %s" % username)
            return True
        except TypeError as e:
            logger.exception("TypeError occured while disabling user %s - failed to disable." % username)
            return False

    @staticmethod
    def update_user_password(username, characterid, password=None):
        logger.debug("Updating smf user %s password" % username)
        cursor = connections['smf'].cursor()
        if not password:
            password = smfManager.generate_random_pass()
        if smfManager.check_user(username):
            username_clean = smfManager.santatize_username(username)
            pwhash = smfManager.gen_hash(username_clean, password)
            logger.debug("Proceeding to update smf user %s password with pwhash starting with %s" % (username, pwhash[0:5]))
            cursor.execute(smfManager.SQL_UPDATE_USER_PASSWORD, [pwhash, username])
            smfManager.add_avatar(username, characterid)
            logger.info("Updated smf user %s password." % username)
            return password
        logger.error("Unable to update smf user %s password - user not found on smf." % username)
        return ""




