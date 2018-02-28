import logging
import random
import string
import re
from django.db import connections
from passlib.hash import bcrypt
from django.conf import settings

logger = logging.getLogger(__name__)


TABLE_PREFIX = getattr(settings, 'IPS4_TABLE_PREFIX', '')


class Ips4Manager:
    SQL_ADD_USER = r"INSERT INTO %score_members (name, email, members_pass_hash, members_pass_salt, " \
                   r"member_group_id) VALUES (%%s, %%s, %%s, %%s, %%s)" % TABLE_PREFIX
    SQL_GET_ID = r"SELECT member_id FROM %score_members WHERE name = %%s" % TABLE_PREFIX
    SQL_UPDATE_PASSWORD = r"UPDATE %score_members SET members_pass_hash = %%s, members_pass_salt = %%s WHERE name = %%s" % TABLE_PREFIX
    SQL_DEL_USER = r"DELETE FROM %score_members WHERE member_id = %%s" % TABLE_PREFIX

    MEMBER_GROUP_ID = 3

    @classmethod
    def add_user(cls, username, email):
        logger.debug("Adding new IPS4 user %s" % username)
        plain_password = cls.__generate_random_pass()
        hash = cls._gen_pwhash(plain_password)
        salt = cls._get_salt(hash)
        group = cls.MEMBER_GROUP_ID
        cursor = connections['ips4'].cursor()
        cursor.execute(cls.SQL_ADD_USER, [username, email, hash, salt, group])
        member_id = cls.get_user_id(username)
        return username, plain_password, member_id

    @staticmethod
    def get_user_id(username):
        cursor = connections['ips4'].cursor()
        cursor.execute(Ips4Manager.SQL_GET_ID, [username])
        row = cursor.fetchone()
        if row is not None:
            logger.debug("Got user id %s for username %s" % (row[0], username))
            return row[0]
        else:
            logger.error("username %s not found. Unable to determine id." % username)
            return None

    @staticmethod
    def __generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def _gen_pwhash(password):
        return bcrypt.using(ident='2y').encrypt(password.encode('utf-8'), rounds=13)

    @staticmethod
    def _get_salt(pw_hash):
        search = re.compile(r"^\$2[a-z]?\$([0-9]+)\$(.{22})(.{31})$")
        match = re.match(search, pw_hash)
        return match.group(2)

    @staticmethod
    def delete_user(id):
        logger.debug("Deleting IPS4 user id %s" % id)
        try:
            cursor = connections['ips4'].cursor()
            cursor.execute(Ips4Manager.SQL_DEL_USER, [id])
            logger.info("Deleted IPS4 user %s" % id)
            return True
        except:
            logger.exception("Failed to delete IPS4 user id %s" % id)
            return False

    @classmethod
    def update_user_password(cls, username):
        logger.debug("Updating IPS4 user id %s password" % id)
        if cls.check_user(username):
            plain_password = Ips4Manager.__generate_random_pass()
            hash = cls._gen_pwhash(plain_password)
            salt = cls._get_salt(hash)
            cursor = connections['ips4'].cursor()
            cursor.execute(cls.SQL_UPDATE_PASSWORD, [hash, salt, username])
            return plain_password
        else:
            logger.error("Unable to update ips4 user %s password" % username)
            return ""

    @staticmethod
    def check_user(username):
        logger.debug("Checking IPS4 username %s" % username)
        cursor = connections['ips4'].cursor()
        cursor.execute(Ips4Manager.SQL_GET_ID, [username])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s on IPS4" % username)
            return True
        logger.debug("User %s not found on IPS4" % username)
        return False

    @classmethod
    def update_custom_password(cls, username, plain_password):
        logger.debug("Updating IPS4 user id %s password" % id)
        if cls.check_user(username):
            hash = cls._gen_pwhash(plain_password)
            salt = cls._get_salt(hash)
            cursor = connections['ips4'].cursor()
            cursor.execute(cls.SQL_UPDATE_PASSWORD, [hash, salt, username])
            return plain_password
        else:
            logger.error("Unable to update ips4 user %s password" % username)
            return ""
