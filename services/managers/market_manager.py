from __future__ import unicode_literals
import logging
import os

from django.db import connections
from passlib.hash import bcrypt

# requires yum install libffi-devel and pip install bcrypt

logger = logging.getLogger(__name__)


class marketManager:
    def __init__(self):
        pass

    SQL_ADD_USER = r"INSERT INTO fos_user (username, username_canonical, email, email_canonical, enabled, salt," \
                   r"password, locked, expired, roles, credentials_expired, characterid, characterName)" \
                   r"VALUES (%s, %s, %s, %s, 1,%s, %s, 0, 0, 'a:0:{}', 0, %s, %s) "
    SQL_GET_USER_ID = r"SELECT id FROM fos_user WHERE username = %s"
    SQL_DISABLE_USER = r"UPDATE fos_user SET enabled = '0' WHERE username = %s"
    SQL_ENABLE_USER = r"UPDATE fos_user SET enabled = '1' WHERE username = %s"
    SQL_UPDATE_PASSWORD = r"UPDATE fos_user SET password = %s, salt = %s WHERE username = %s"
    SQL_CHECK_EMAIL = r"SELECT email FROM fos_user WHERE email = %s"
    SQL_CHECK_USERNAME = r"SELECT username FROM fos_user WHERE username = %s"
    SQL_UPDATE_USER = r"UPDATE fos_user SET password = %s, salt = %s, enabled = '1' WHERE username = %s"

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def check_username(username):
        logger.debug("Checking alliance market username %s" % username)
        cursor = connections['market'].cursor()
        cursor.execute(marketManager.SQL_CHECK_USERNAME, [marketManager.__santatize_username(username)])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s on alliance market" % username)
            return True
        logger.debug("User %s not found on alliance market" % username)
        return False

    @staticmethod
    def check_user_email(username, email):
        logger.debug("Checking if alliance market email exists for user %s" % username)
        cursor = connections['market'].cursor()
        cursor.execute(marketManager.SQL_CHECK_EMAIL, [email])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s email address on alliance market" % username)
            return True
        logger.debug("User %s email address not found on alliance market" % username)
        return False

    @staticmethod
    def add_user(username, email, characterid, charactername):
        logger.debug("Adding new market user %s" % username)
        plain_password = marketManager.__generate_random_pass()
        hash = bcrypt.encrypt(plain_password, rounds=13)
        hash_result = hash
        rounds_striped = hash_result.strip('$2a$13$')
        salt = rounds_striped[:22]
        username_clean = marketManager.__santatize_username(username)
        if not marketManager.check_username(username):
            if not marketManager.check_user_email(username, email):
                try:
                    logger.debug("Adding user %s to alliance market" % username)
                    cursor = connections['market'].cursor()
                    cursor.execute(marketManager.SQL_ADD_USER, [username_clean, username_clean, email, email, salt,
                                                                hash, characterid, charactername])
                    return username_clean, plain_password
                except:
                    logger.debug("Unsuccessful attempt to add market user %s" % username)
                    return "", ""
            else:
                logger.debug("Alliance market email %s already exists Updating instead" % email)
                username_clean, password = marketManager.update_user_info(username)
                return username_clean, password
        else:
            logger.debug("Alliance market username %s already exists Updating instead" % username)
            username_clean, password = marketManager.update_user_info(username)
            return username_clean, password

    @staticmethod
    def disable_user(username):
        logger.debug("Disabling alliance market user %s " % username)
        cursor = connections['market'].cursor()
        cursor.execute(marketManager.SQL_DISABLE_USER, [username])
        return True

    @staticmethod
    def update_custom_password(username, plain_password):
        logger.debug("Updating alliance market user %s password" % username)
        if marketManager.check_username(username):
            username_clean = marketManager.__santatize_username(username)
            hash = bcrypt.encrypt(plain_password, rounds=13)
            hash_result = hash
            rounds_striped = hash_result.strip('$2a$13$')
            salt = rounds_striped[:22]
            cursor = connections['market'].cursor()
            cursor.execute(marketManager.SQL_UPDATE_PASSWORD, [hash, salt, username_clean])
            return plain_password
        else:
            logger.error("Unable to update alliance market user %s password" % username)
            return ""

    @staticmethod
    def update_user_password(username):
        logger.debug("Updating alliance market user %s password" % username)
        if marketManager.check_username(username):
            username_clean = marketManager.__santatize_username(username)
            plain_password = marketManager.__generate_random_pass()
            hash = bcrypt.encrypt(plain_password, rounds=13)
            hash_result = hash
            rounds_striped = hash_result.strip('$2a$13$')
            salt = rounds_striped[:22]
            cursor = connections['market'].cursor()
            cursor.execute(marketManager.SQL_UPDATE_PASSWORD, [hash, salt, username_clean])
            return plain_password
        else:
            logger.error("Unable to update alliance market user %s password" % username)
            return ""

    @staticmethod
    def update_user_info(username):
        logger.debug("Updating alliance market user %s" % username)
        try:
            username_clean = marketManager.__santatize_username(username)
            plain_password = marketManager.__generate_random_pass()
            hash = bcrypt.encrypt(plain_password, rounds=13)
            hash_result = hash
            rounds_striped = hash_result.strip('$2a$13$')
            salt = rounds_striped[:22]
            cursor = connections['market'].cursor()
            cursor.execute(marketManager.SQL_UPDATE_USER, [hash, salt, username_clean])
            return username_clean, plain_password
        except:
            logger.debug("Alliance market update user failed for %s" % username)
            return "", ""
