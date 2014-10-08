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
        self.dbcursor = connections['mumble'].cursor()

    def __santatize_username(self, username):
        sanatized = username.replace(" ", "_")
        return sanatized

    def __generate_random_pass(self):
        return os.urandom(8).encode('hex')

    def __generate_username(self, username, corp_ticker):
        return "["+corp_ticker+"]"+username

    def _gen_pwhash(self, password):
        return hashlib.sha1(password).hexdigest()

    def get_user_id_by_name(self, name):
        self.dbcursor.execute(self.SQL_SELECT_GET_USER_ID_BY_NAME, [name, settings.MUMBLE_SERVER_ID])
        row = self.dbcursor.fetchone()
        if row:
            return row[0]

    def create_user(self, corp_ticker, username):

        username_clean = self.__generate_username(self.__santatize_username(username),  corp_ticker)
        password = self.__generate_random_pass()
        pwhash = self._gen_pwhash(password)

        try:
            self.dbcursor.execute(self.SQL_SELECT_MAX_ID)
            user_id = self.dbcursor.fetchone()[0]

            self.dbcursor.execute(self.SQL_CREATE_USER,
                                  [settings.MUMBLE_SERVER_ID, user_id, username_clean,
                                   pwhash])

            return username_clean, password
        except:
            return "", ""

    def check_user_exist(self, username):

        self.dbcursor.execute(self.SQL_CHECK_USER_EXIST,
                              [username, settings.MUMBLE_SERVER_ID])

        row = self.dbcursor.fetchone()
        if row and row[0].lower() == username.lower():
            return True
        return False

    def delete_user(self, username):

        if self.check_user_exist(username):
            try:

                self.dbcursor.execute(self.SQL_DELETE_USER,
                                      [username, settings.MUMBLE_SERVER_ID])
                return True
            except:
                return False

        return False

    def update_user_password(self, username):

        password = self.__generate_random_pass()
        pwhash = self._gen_pwhash(password)

        if self.check_user_exist(username):
            try:

                self.dbcursor.execute(self.SQL_UPDATE_USER_PASSWORD,
                                      [pwhash, username, settings.MUMBLE_SERVER_ID])
                return password
            except:
                return ""

        return ""