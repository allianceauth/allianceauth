import random
from passlib.apps import phpbb3_context
from django.db import connections


class Phpbb3Manager():
    
    SQL_ADD_USER = r"INSERT INTO phpbb_users (username, username_clean, " \
                   r"user_password, user_email, group_id , user_permissions, " \
                   r"user_sig, user_occ, user_interests) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    SQL_DIS_USER = r"DELETE FROM phpbb_user_groups where user_id = " \
                   r"(SELECT user_id FROM phpbb_users WHERE username = %s)"

    SQL_CHECK_USER = r"SELECT user_id from phpbb_users WHERE username = %s"

    SQL_ADD_USER_GROUP = r"INSERT INTO phpbb_user_group (group_id, user_id, user_pending) VALUES (%s, %s, %s)"

    SQL_GET_GROUP = r"SELECT group_id from phpbb_groups WHERE group_name = %s"

    SQL_ADD_GROUP = r"INSERT INTO phpbb_groups (group_name) VALUES (%s)"
    
    def __init__(self):
        pass
    
    def _gen_salt(self):
        return "%x" % random.randint(0, 2147483647)

    def _gen_hash(self, password):
        return phpbb3_context.encrypt(password)
    
    def add_user(self, username, password, email, groups):
        
        cursor = connections['phpbb3'].cursor()
        
        """ Add a user """
        username_clean = username.lower()
        pwhash = self._gen_hash(password)
        cursor.execute(self.SQL_ADD_USER, [username, username_clean, pwhash, email, 2, "", "","", ""])
        self.update_groups(username,groups)
        return { 'username': username, 'password': password }

    def update_groups(self, username, groups):
        cursor = connections['phpbb3'].cursor()

        cursor.execute(self.SQL_CHECK_USER, [username])
        row = cursor.fetchone()
        userid = row[0]
        for group in groups:
            cursor.execute(self.SQL_GET_GROUP, [group])
            row = cursor.fetchone()
            print row
            if not row:
                cursor.execute(self.SQL_ADD_GROUP, [group])
                cursor.execute(self.SQL_GET_GROUP, [group])
                row = cursor.fetchone()

            cursor.execute(self.SQL_ADD_USER_GROUP, [row[0], userid,0])
    
    def check_user(self, username):
        cursor = connections['phpbb3'].cursor()
        """ Check if the username exists """
        cursor.execute(self.SQL_CHECK_USER, [username])
        row = cursor.fetchone()
        if row:
            return True        
        return False