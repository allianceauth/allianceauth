import os
import hashlib
from django.db import connections
from django.conf import settings


class MumbleManager:

    SQL_SELECT_MAX_ID = r"SELECT max(user_id)+1 as next_id from murmur_users"
    SQL_CREATE_USER = r"INSERT INTO murmur_users (server_id, user_id, name, pw) VALUES (%s, %s, %s, %s)"
    SQL_SELECT_GET_USER_ID_BY_NAME = r"SELECT user_id from murmur_users WHERE name = %s AND server_id = %s"
    SQL_CHECK_USER_EXIST = r"SELECT name from murmur_users WHERE name = %s AND server_id = %s"
    SQL_DELETE_USER = r"DELETE FROM murmur_users WHERE name = %s AND server_id = %s"
    SQL_UPDATE_USER_PASSWORD = r"UPDATE murmur_users SET pw = %s WHERE name = %s AND server_id = %s"

    def __init__(self):
        pass

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def __generate_username(username, corp_ticker):
        return "["+corp_ticker+"]"+username

    @staticmethod
    def _gen_pwhash(password):
        return hashlib.sha1(password).hexdigest()

    @staticmethod
    def get_user_id_by_name(name):
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_SELECT_GET_USER_ID_BY_NAME, [name, settings.MUMBLE_SERVER_ID])
        row = dbcursor.fetchone()
        if row:
            return row[0]

    @staticmethod
    def create_user(corp_ticker, username):
        dbcursor = connections['mumble'].cursor()
        username_clean = MumbleManager.__generate_username(MumbleManager.__santatize_username(username), corp_ticker)
        password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)

        try:
            dbcursor.execute(MumbleManager.SQL_SELECT_MAX_ID)
            user_id = dbcursor.fetchone()[0]

            dbcursor.execute(MumbleManager.SQL_CREATE_USER,
                             [settings.MUMBLE_SERVER_ID, user_id, username_clean, pwhash])

            return username_clean, password
        except:

            return "", ""

    @staticmethod
    def check_user_exist(username):
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_CHECK_USER_EXIST,
                         [username, settings.MUMBLE_SERVER_ID])

        row = dbcursor.fetchone()
        if row and row[0].lower() == username.lower():
            return True
        return False

    @staticmethod
    def delete_user(username):
        dbcursor = connections['mumble'].cursor()
        if MumbleManager.check_user_exist(username):
            try:

                dbcursor.execute(MumbleManager.SQL_DELETE_USER,
                                 [username, settings.MUMBLE_SERVER_ID])
                return True
            except:
                return False

        return False

    @staticmethod
    def update_user_password(username):
        dbcursor = connections['mumble'].cursor()
        password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)

        if MumbleManager.check_user_exist(username):
            try:

                dbcursor.execute(MumbleManager.SQL_UPDATE_USER_PASSWORD,
                                 [pwhash, username, settings.MUMBLE_SERVER_ID])
                return password
            except:
                return ""

        return ""