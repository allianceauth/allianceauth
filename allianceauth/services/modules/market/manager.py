import logging
import random
import string
import re

from django.db import connections
from passlib.hash import bcrypt
from django.conf import settings

# requires yum install libffi-devel and pip install bcrypt

logger = logging.getLogger(__name__)


TABLE_PREFIX = getattr(settings, 'MARKET_TABLE_PREFIX', 'fos_')


class MarketManager:
    def __init__(self):
        pass

    SQL_ADD_USER = r"INSERT INTO %suser (username, username_canonical, email, email_canonical, enabled, salt," \
                   r"password, locked, expired, roles, credentials_expired, characterid, characterName)" \
                   r"VALUES (%%s, %%s, %%s, %%s, 1,%%s, %%s, 0, 0, 'a:0:{}', 0, %%s, %%s) " % TABLE_PREFIX
    SQL_GET_USER_ID = r"SELECT id FROM %suser WHERE username = %%s" % TABLE_PREFIX
    SQL_DISABLE_USER = r"UPDATE %suser SET enabled = '0' WHERE username = %%s" % TABLE_PREFIX
    SQL_ENABLE_USER = r"UPDATE %suser SET enabled = '1' WHERE username = %%s" % TABLE_PREFIX
    SQL_UPDATE_PASSWORD = r"UPDATE %suser SET password = %%s, salt = %%s WHERE username = %%s" % TABLE_PREFIX
    SQL_CHECK_EMAIL = r"SELECT email FROM %suser WHERE email = %%s" % TABLE_PREFIX
    SQL_CHECK_USERNAME = r"SELECT username FROM %suser WHERE username = %%s" % TABLE_PREFIX
    SQL_UPDATE_USER = r"UPDATE %suser SET password = %%s, salt = %%s, enabled = '1' WHERE username = %%s" % TABLE_PREFIX

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

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

    @classmethod
    def check_username(cls, username):
        logger.debug("Checking alliance market username %s" % username)
        cursor = connections['market'].cursor()
        cursor.execute(cls.SQL_CHECK_USERNAME, [cls.__santatize_username(username)])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s on alliance market" % username)
            return True
        logger.debug("User %s not found on alliance market" % username)
        return False

    @classmethod
    def check_user_email(cls, username, email):
        logger.debug("Checking if alliance market email exists for user %s" % username)
        cursor = connections['market'].cursor()
        cursor.execute(cls.SQL_CHECK_EMAIL, [email])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s email address on alliance market" % username)
            return True
        logger.debug("User %s email address not found on alliance market" % username)
        return False

    @classmethod
    def add_user(cls, username, email, characterid, charactername):
        logger.debug("Adding new market user %s" % username)
        plain_password = cls.__generate_random_pass()
        hash = cls._gen_pwhash(plain_password)
        salt = cls._get_salt(hash)
        username_clean = cls.__santatize_username(username)
        if not cls.check_username(username):
            if not cls.check_user_email(username, email):
                try:
                    logger.debug("Adding user %s to alliance market" % username)
                    cursor = connections['market'].cursor()
                    cursor.execute(cls.SQL_ADD_USER, [username_clean, username_clean, email, email, salt,
                                                                hash, characterid, charactername])
                    return username_clean, plain_password
                except:
                    logger.debug("Unsuccessful attempt to add market user %s" % username)
                    return "", ""
            else:
                logger.debug("Alliance market email %s already exists Updating instead" % email)
                username_clean, password = cls.update_user_info(username)
                return username_clean, password
        else:
            logger.debug("Alliance market username %s already exists Updating instead" % username)
            username_clean, password = cls.update_user_info(username)
            return username_clean, password

    @classmethod
    def disable_user(cls, username):
        logger.debug("Disabling alliance market user %s " % username)
        cursor = connections['market'].cursor()
        cursor.execute(cls.SQL_DISABLE_USER, [username])
        return True

    @classmethod
    def update_custom_password(cls, username, plain_password):
        logger.debug("Updating alliance market user %s password" % username)
        if cls.check_username(username):
            username_clean = cls.__santatize_username(username)
            hash = cls._gen_pwhash(plain_password)
            salt = cls._get_salt(hash)
            cursor = connections['market'].cursor()
            cursor.execute(cls.SQL_UPDATE_PASSWORD, [hash, salt, username_clean])
            return plain_password
        else:
            logger.error("Unable to update alliance market user %s password" % username)
            return ""

    @classmethod
    def update_user_password(cls, username):
        logger.debug("Updating alliance market user %s password" % username)
        if cls.check_username(username):
            username_clean = cls.__santatize_username(username)
            plain_password = cls.__generate_random_pass()
            hash = cls._gen_pwhash(plain_password)
            salt = cls._get_salt(hash)
            cursor = connections['market'].cursor()
            cursor.execute(cls.SQL_UPDATE_PASSWORD, [hash, salt, username_clean])
            return plain_password
        else:
            logger.error("Unable to update alliance market user %s password" % username)
            return ""

    @classmethod
    def update_user_info(cls, username):
        logger.debug("Updating alliance market user %s" % username)
        try:
            username_clean = cls.__santatize_username(username)
            plain_password = cls.__generate_random_pass()
            hash = cls._gen_pwhash(plain_password)
            salt = cls._get_salt(hash)
            cursor = connections['market'].cursor()
            cursor.execute(cls.SQL_UPDATE_USER, [hash, salt, username_clean])
            return username_clean, plain_password
        except:
            logger.debug("Alliance market update user failed for %s" % username)
            return "", ""
