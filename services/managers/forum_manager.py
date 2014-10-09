import os
from passlib.apps import phpbb3_context
from django.db import connections


class ForumManager:
    
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
        pass

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def __gen_hash(password):
        return phpbb3_context.encrypt(password)

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    @staticmethod
    def add_user(username, email, groups):
        cursor = connections['phpbb3'].cursor()

        username_clean = ForumManager.__santatize_username(username)
        password = ForumManager.__generate_random_pass()
        pwhash = ForumManager.__gen_hash(password)

        # check if the username was simply revoked
        if ForumManager.check_user(username_clean):
            ForumManager.__update_user_info(username_clean, email, pwhash)
        else:
            try:
                cursor.execute(ForumManager.SQL_ADD_USER, [username_clean, username_clean, pwhash,
                                                           email, 2, "", "", "", ""])
                ForumManager.update_groups(username_clean, groups)
            except:
                pass

        return username_clean, password

    @staticmethod
    def disable_user(username):
        cursor = connections['phpbb3'].cursor()

        password = ForumManager.__gen_hash(ForumManager.__generate_random_pass())
        revoke_email = "revoked@the99eve.com"
        try:
            pwhash = ForumManager.__gen_hash(password)
            cursor.execute(ForumManager.SQL_DIS_USER, [revoke_email, pwhash, username])
            return True
        except TypeError as e:
            print e
            return False

    @staticmethod
    def delete_user(username):
        cursor = connections['phpbb3'].cursor()

        if ForumManager.check_user(username):
            cursor.execute(ForumManager.SQL_DEL_USER, [username])
            return True
        return False

    @staticmethod
    def update_groups(username, groups):
        cursor = connections['phpbb3'].cursor()

        cursor.execute(ForumManager.SQL_CHECK_USER, [username])
        row = cursor.fetchone()
        userid = row[0]
        for group in groups:
            cursor.execute(ForumManager.SQL_GET_GROUP, [group])
            row = cursor.fetchone()
            print row
            if not row:
                cursor.execute(ForumManager.SQL_ADD_GROUP, [group])
                cursor.execute(ForumManager.SQL_GET_GROUP, [group])
                row = cursor.fetchone()

            cursor.execute(ForumManager.SQL_ADD_USER_GROUP, [row[0], userid,0])

    @staticmethod
    def check_user(username):
        cursor = connections['phpbb3'].cursor()
        """ Check if the username exists """
        cursor.execute(ForumManager.SQL_CHECK_USER, [ForumManager.__santatize_username(username)])
        row = cursor.fetchone()
        if row:
            return True        
        return False

    @staticmethod
    def update_user_password(username):
        cursor = connections['phpbb3'].cursor()
        password = ForumManager.__generate_random_pass()
        if ForumManager.check_user(username):
            pwhash = ForumManager.__gen_hash(password)
            cursor.execute(ForumManager.SQL_UPDATE_USER_PASSWORD, [pwhash, username])
            return password

        return ""

    @staticmethod
    def __update_user_info(username, email, password):
        cursor = connections['phpbb3'].cursor()
        try:
            cursor.execute(ForumManager.SQL_DIS_USER, [email, password, username])
        except:
            pass