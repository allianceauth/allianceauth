from __future__ import unicode_literals
import logging
import os
from django.db import connections
from passlib.hash import bcrypt

logger = logging.getLogger(__name__)


class Ips4Manager:
    SQL_ADD_USER = r"INSERT INTO core_members (name, email, members_pass_hash, members_pass_salt, " \
                   r"member_group_id) VALUES (%s, %s, %s, %s, %s)"
    SQL_GET_ID = r"SELECT member_id FROM core_members WHERE name = %s"
    SQL_UPDATE_PASSWORD = r"UPDATE core_members SET members_pass_hash = %s, members_pass_salt = %s WHERE name = %s"
    SQL_DEL_USER = r"DELETE FROM core_members WHERE member_id = %s"

    MEMBER_GROUP_ID = 3

    @staticmethod
    def add_user(username, email):
        logger.debug("Adding new IPS4 user %s" % username)
        plain_password = Ips4Manager.__generate_random_pass()
        hash = bcrypt.encrypt(plain_password, rounds=13)
        hash_result = hash
        rounds_striped = hash_result.strip('$2a$13$')
        salt = rounds_striped[:22]
        group = Ips4Manager.MEMBER_GROUP_ID
        cursor = connections['ips4'].cursor()
        cursor.execute(Ips4Manager.SQL_ADD_USER, [username, email, hash, salt, group])
        member_id = Ips4Manager.get_user_id(username)
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
        return os.urandom(8).encode('hex')

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

    @staticmethod
    def update_user_password(username):
        logger.debug("Updating IPS4 user id %s password" % id)
        if Ips4Manager.check_user(username):
            plain_password = Ips4Manager.__generate_random_pass()
            hash = bcrypt.encrypt(plain_password, rounds=13)
            hash_result = hash
            rounds_striped = hash_result.strip('$2a$13$')
            salt = rounds_striped[:22]
            cursor = connections['ips4'].cursor()
            cursor.execute(Ips4Manager.SQL_UPDATE_PASSWORD, [hash, salt, username])
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

    @staticmethod
    def update_custom_password(username, plain_password):
        logger.debug("Updating IPS4 user id %s password" % id)
        if Ips4Manager.check_user(username):
            hash = bcrypt.encrypt(plain_password, rounds=13)
            hash_result = hash
            rounds_striped = hash_result.strip('$2a$13$')
            salt = rounds_striped[:22]
            cursor = connections['ips4'].cursor()
            cursor.execute(Ips4Manager.SQL_UPDATE_PASSWORD, [hash, salt, username])
            return plain_password
        else:
            logger.error("Unable to update ips4 user %s password" % username)
            return ""
