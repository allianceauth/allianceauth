import os
import sys
from passlib.apps import phpbb3_context
from django.db import connections


class Phpbb3Manager():
    
    SQL_ADD_USER = r"INSERT INTO phpbb_users (username, username_clean, " \
                   r"user_password, user_email, group_id , user_permissions, " \
                   r"user_sig, user_occ, user_interests) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    SQL_DEL_USER = r"DELETE FROM phpbb_users where username = %s"

    SQL_DIS_USER = r"UPDATE phpbb_users SET user_email= %s, user_password=%s WHERE username = %s"

    SQL_CHECK_USER = r"SELECT user_id from phpbb_users WHERE username = %s"

    SQL_ADD_USER_GROUP = r"INSERT INTO phpbb_user_group (group_id, user_id, user_pending) VALUES (%s, %s, %s)"

    SQL_GET_GROUP = r"SELECT group_id from phpbb_groups WHERE group_name = %s"

    SQL_ADD_GROUP = r"INSERT INTO phpbb_groups (group_name) VALUES (%s)"

    SQL_UPDATE_USER_PASSWORD = r"UPDATE phpbb_users SET user_password = %s WHERE username = %s"

    def __init__(self):
        self.cursor = connections['phpbb3'].cursor()

    def __generate_random_pass(self):
        return os.urandom(8).encode('hex')

    def __gen_hash(self, password):
        return phpbb3_context.encrypt(password)

    def __santatize_username(self, username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    def add_user(self, username, email, groups):
        username_clean = self.__santatize_username(username)
        password = self.__generate_random_pass()
        pwhash = self.__gen_hash(password)

        # check if the username was simply revoked
        if self.check_user(username_clean):
            self.__update_user_info(username_clean, email, pwhash)
        else:
            try:
                self.cursor.execute(self.SQL_ADD_USER, [username_clean, username_clean, pwhash, email, 2, "", "", "", ""])
                self.update_groups(username_clean, groups)
            except:
                pass

        return username_clean, password

    def disable_user(self, username):
        password = self.__gen_hash(self.__generate_random_pass())
        revoke_email = "revoked@the99eve.com"
        try:
            pwhash = self.__gen_hash(password)
            self.cursor.execute(self.SQL_DIS_USER, [revoke_email, pwhash, username])
            return True
        except TypeError as e:
            print e
            return False

    def delete_user(self, username):
        if self.check_user(username):
            self.cursor.execute(self.SQL_DEL_USER, [username])
            return True
        return False

    def update_groups(self, username, groups):
        self.cursor.execute(self.SQL_CHECK_USER, [username])
        row = self.cursor.fetchone()
        userid = row[0]
        for group in groups:
            self.cursor.execute(self.SQL_GET_GROUP, [group])
            row = self.cursor.fetchone()
            print row
            if not row:
                self.cursor.execute(self.SQL_ADD_GROUP, [group])
                self.cursor.execute(self.SQL_GET_GROUP, [group])
                row = self.cursor.fetchone()

            self.cursor.execute(self.SQL_ADD_USER_GROUP, [row[0], userid,0])
    
    def check_user(self, username):
        cursor = connections['phpbb3'].cursor()
        """ Check if the username exists """
        cursor.execute(self.SQL_CHECK_USER, [self.__santatize_username(username)])
        row = cursor.fetchone()
        if row:
            return True        
        return False

    def update_user_password(self, username):
        password = self.__generate_random_pass()
        if self.check_user(username):
            pwhash = self.__gen_hash(password)
            self.cursor.execute(self.SQL_UPDATE_USER_PASSWORD, [pwhash, username])
            return password

        return ""

    def __update_user_info(self, username, email, password):
        try:
            self.cursor.execute(self.SQL_DIS_USER, [email, password, username])
        except:
            pass