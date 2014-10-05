import uuid
import hashlib
import random
from django.db import connections
from django.conf import settings

class MumbleManager:

    def __init__(self):
        self.dbcursor = connections['mumble'].cursor()

    @staticmethod
    def _gen_pwhash(password):
        return hashlib.sha1(password).hexdigest()

    def get_user_id_by_name(self, name):
        self.dbcursor.execute(r"SELECT user_id from murmur_users WHERE name = %s AND server_id = %s",
                              [name, settings.MUMBLE_SERVER_ID])
        row = self.dbcursor.fetchone()
        if row:
            return row[0]

    def create_user(self, username, password):
        """ Add a user """
        self.dbcursor.execute(r"SELECT max(user_id)+1 as next_id from murmur_users")
        user_id = self.dbcursor.fetchone()[0]

        self.dbcursor.execute(r"INSERT INTO murmur_users (server_id, user_id, name, pw) VALUES (%s, %s, %s, %s)",
                              [settings.MUMBLE_SERVER_ID, user_id, self.__santatize_username(username), self._gen_pwhash(password)])

        return {'username': username, 'password': password }

    def check_user_exist(self, username):
        """ Check if the username exists """
        self.dbcursor.execute(r"SELECT name from murmur_users WHERE name = %s AND server_id = %s",
                              [username, settings.MUMBLE_SERVER_ID])

        row = self.dbcursor.fetchone()
        if row and row[0].lower() == username.lower():
            return True
        return False

    def delete_user(self, uid):
        """ Delete a user """
        id = self.get_user_id_by_name(uid)
        self.dbcursor.execute(r"DELETE FROM murmur_users WHERE user_id = %s AND server_id = %s",
                              [id, settings.MUMBLE_SERVER_ID])
        return True

    def __santatize_username(self, username):
        sanatized = username.replace(" ","_")
        return sanatized.lower()