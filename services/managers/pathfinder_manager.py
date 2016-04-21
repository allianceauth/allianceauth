import logging
from django.conf import settings
import requests
import os
from django.db import connections
from passlib.hash import bcrypt
from eveonline.managers import EveManager
from authentication.managers import AuthServicesInfo
from eveonline.models import EveCharacter
from eveonline.models import EveApiKeyPair

logger = logging.getLogger(__name__)

class pathfinderManager:

    SQL_ADD_USER = r"INSERT INTO user (name, email, password, active) VALUES (%s, %s, %s, %s)"
    SQL_ADD_API = r"INSERT INTO user_api (userid, keyid, vCode, active) VALUES (%s, %s, %s, %s)"
    SQL_ADD_CHARACTER = r"INSERT INTO user_character (userid, apiId, characterId, isMain) VALUES (%s, %s, %s, %s)"
    SQL_GET_APIID = r"SELECT id, keyId  FROM user_api WHERE userId = %s"
    SQL_GET_USERID = r"SELECT id FROM user WHERE name = %s"
    SQL_DISABLE_USER = r"UPDATE user SET active = '0' WHERE name = %s"
    SQL_UPDATE_USER = r"UPDATE user SET active = '1', password = %s WHERE name = %s"
    SQL_CHECK_USER = r"SELECT name FROM user WHERE name = %s"
    SQL_CHECK_EMAIL = r"SELECT email from user WHERE email = %s"
    SQL_SET_MAIN = r"UPDATE user_character SET isMain = 1 WHERE characterId = %s"


    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def check_username(username):
        logger.debug("Checking for pathfinder username %s" % username)
        cursor = connections['pathfinder'].cursor()
        cursor.execute(pathfinderManager.SQL_CHECK_USER, [pathfinderManager.__santatize_username(username)])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s on pathfinder" % username)
            return True
        logger.debug("User %s not found on pathfinder" % username)
        return False

    @staticmethod
    def update_user_info(username):
        logger.debug("Updating pathfinder user %s" % username)
        try:
            username_clean = pathfinderManager.__santatize_username(username)
            plain_password = pathfinderManager.__generate_random_pass()
            passwd = bcrypt.encrypt(plain_password, rounds=10)
            cursor = connections['pathfinder'].cursor()
            cursor.execute(pathfinderManager.SQL_UPDATE_USER, [passwd, username_clean])
            return username_clean, plain_password
        except:
            logger.debug("Pathfinder update user failed for %s" % username)
            return "", ""

    @staticmethod
    def update_custom_password(username, plain_password):
        logger.debug("Updating pathfinder user id %s password" % username)
        if pathfinderManager.check_username(username):
            username_clean = pathfinderManager.__santatize_username(username)
            passwd = bcrypt.encrypt(plain_password, rounds=10)
            cursor = connections['pathfinder'].cursor()
            cursor.execute(pathfinderManager.SQL_UPDATE_USER, [passwd, username_clean])
            return plain_password
        else:
            logger.error("Unable to update ips4 user %s password" % username)
            return ""

    @staticmethod
    def disable_user(username):
        logger.debug("Disabling user %s" % username)
        if pathfinderManager.check_username(username) == True:
            try:
                cursor = connections['pathfinder'].cursor()
                cursor.execute(pathfinderManager.SQL_DISABLE_USER, [pathfinderManager.__santatize_username(username)])
                return True
            except:
                logger.debug("User %s not found cannot disable" % username)



    @staticmethod
    def add_user(username, email, charactername):
        logger.debug("Adding new pathfinder user %s" % username)
        plain_password = pathfinderManager.__generate_random_pass()
        passwd = bcrypt.encrypt(plain_password, rounds=10)
        username_clean = pathfinderManager.__santatize_username(username)
        auth_id = pathfinderManager.get_authid_by_username(charactername)

        if pathfinderManager.check_username(username)== False:
            if pathfinderManager.check_email(username, email) == False:
                try:
                    logger.debug("Adding user %s to pathfinder" % username)
                    cursor = connections['pathfinder'].cursor()
                    cursor.execute(pathfinderManager.SQL_ADD_USER, [username_clean,email, passwd, '1'])
                    path_id = pathfinderManager.get_pathfinder_user_id(username_clean)
                    api_keys = pathfinderManager.get_api_key_pairs(auth_id)
                    main_character = AuthServicesInfo.objects.get(user=auth_id).main_char_id

                    for keyId, key in api_keys.items():
                        cursor.execute(pathfinderManager.SQL_ADD_API, [path_id, keyId, key, '1'])

                    char_apis  = pathfinderManager.get_char_id(auth_id)

                    for c,a in char_apis.items():
                        cursor.execute(pathfinderManager.SQL_ADD_CHARACTER, [path_id, (pathfinderManager.get_pathfinder_api_id(username, path_id)), c, '0'])

                    pathfinderManager.set_main_char(username, main_character)
                    return username_clean, plain_password

                except:
                    logger.debug("Unsuccessful attempt at adding user %s to pathfinder on add_user" % username)
                    return "",""
            else:
                logger.debug("pathfinder username %s already exists Updating instead" % username)
                username_clean, password = pathfinderManager.update_user_info(username)
                return username_clean, password
        else:
            logger.debug("pathfinder username %s already exists Updating instead" % username)
            username_clean, password = pathfinderManager.update_user_info(username)
            return username_clean, password

    @staticmethod
    def set_main_char (username, main_character):
        try:
            cursor = connections['pathfinder'].cursor()
            cursor.execute(pathfinderManager.SQL_SET_MAIN, [main_character])
        except:
            logger.debug("Failed setting main character for user %s"% username)
            return ""

    @staticmethod
    def get_api_key_pairs(user_id):
        char = EveCharacter.objects.all().filter(user_id=user_id)
        api_list = dict()
        for c in char:
            api_pair = EveApiKeyPair.objects.get(api_id=c.api_id)
            api_list[api_pair.api_id] = api_pair.api_key
        return api_list

    @staticmethod
    def get_char_id(auth_id):
        char = EveCharacter.objects.all().filter(user_id=auth_id)
        char_list = dict()
        for c in char:
            char_list[c.character_id] = c.api_id
        logger.debug("printing char list %s" % char_list)
        return char_list

    @staticmethod
    def get_authid_by_username(username):
        authid = EveCharacter.objects.get(character_name=username).user_id
        return authid

    @staticmethod
    def get_pathfinder_user_id(username):
        cursor = connections['pathfinder'].cursor()
        cursor.execute(pathfinderManager.SQL_GET_USERID, [username])
        row = cursor.fetchone()
        if row:
            logger.debug("Pathfinder ID for user %s is %s" % (username, row[0]))
            return int(row[0])
        else:
            logger.debug("failed to get pathfinder ID for user %s" % username)
            return ""

    @staticmethod
    def get_pathfinder_api_id(username, path_id):
        cursor = connections['pathfinder'].cursor()
        cursor.execute(pathfinderManager.SQL_GET_APIID, [path_id])
        row = cursor.fetchone()
        if row:
            logger.debug("Pathfinder API ID for user %s is %s" % (username, row[0]))
            return int(row[0])
        else:
            logger.debug("failed to get pathfinder API ID for user %s" % username)
            return ""

    @staticmethod
    def check_email(username, email):
        logger.debug("Checking if email %s exists for username %s" % (email,username))
        cursor = connections['pathfinder'].cursor()
        cursor.execute(pathfinderManager.SQL_CHECK_EMAIL, [email])
        row = cursor.fetchone()
        if row:
            logger.debug("Found user %s email on pathfinder" % username)
            return True
        logger.debug("User %s email not found on pathfinder" % username)
        return False