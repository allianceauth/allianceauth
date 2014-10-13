import os
import calendar
from datetime import datetime
from passlib.apps import phpbb3_context
from django.db import connections


class ForumManager:
    
    SQL_ADD_USER = r"INSERT INTO phpbb_users (username, username_clean, " \
                   r"user_password, user_email, group_id, user_regdate, user_permissions, " \
                   r"user_sig, user_occ, user_interests) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    SQL_DEL_USER = r"DELETE FROM phpbb_users where username = %s"

    SQL_DIS_USER = r"UPDATE phpbb_users SET user_email= %s, user_password=%s WHERE username = %s"

    SQL_USER_ID_FROM_USERNAME = r"SELECT user_id from phpbb_users WHERE username = %s"

    SQL_ADD_USER_GROUP = r"INSERT INTO phpbb_user_group (group_id, user_id, user_pending) VALUES (%s, %s, %s)"

    SQL_GET_GROUP_ID = r"SELECT group_id from phpbb_groups WHERE group_name = %s"

    SQL_ADD_GROUP = r"INSERT INTO phpbb_groups (group_name,group_desc,group_legend) VALUES (%s,%s,0)"

    SQL_UPDATE_USER_PASSWORD = r"UPDATE phpbb_users SET user_password = %s WHERE username = %s"

    SQL_REMOVE_USER_GROUP = r"DELETE FROM phpbb_user_group WHERE user_id=%s AND group_id=%s "

    SQL_GET_ALL_GROUPS = r"SELECT group_id, group_name FROM phpbb_groups"

    SQL_GET_USER_GROUPS = r"SELECT phpbb_groups.group_name FROM phpbb_groups , phpbb_user_group WHERE " \
                          r"phpbb_user_group.group_id = phpbb_groups.group_id AND user_id=%s"

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
    def __get_group_id(groupname):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(ForumManager.SQL_GET_GROUP_ID, [groupname])
        row = cursor.fetchone()

        return row[0]

    @staticmethod
    def __get_user_id(username):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(ForumManager.SQL_USER_ID_FROM_USERNAME, [username])
        row = cursor.fetchone()
        return row[0]

    @staticmethod
    def __get_all_groups():
        cursor = connections['phpbb3'].cursor()
        cursor.execute(ForumManager.SQL_GET_ALL_GROUPS)
        rows = cursor.fetchall()
        out = {}
        for row in rows:
            out[row[1]] = row[0]

        return out

    @staticmethod
    def __get_user_groups(userid):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(ForumManager.SQL_GET_USER_GROUPS, [userid])
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def __get_current_utc_date():
        d = datetime.utcnow()
        unixtime = calendar.timegm(d.utctimetuple())
        return unixtime

    @staticmethod
    def __create_group(groupname):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(ForumManager.SQL_ADD_GROUP, [groupname,groupname])
        return ForumManager.__get_group_id(groupname)

    @staticmethod
    def __add_user_to_group(userid, groupid):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(ForumManager.SQL_ADD_USER_GROUP, [groupid, userid, 0])

    @staticmethod
    def __remove_user_from_group(userid, groupid):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(ForumManager.SQL_REMOVE_USER_GROUP, [userid, groupid])

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
                                                           email, 2, ForumManager.__get_current_utc_date(),
                                                           "", "", "", ""])
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
        userid = ForumManager.__get_user_id(username)
        forum_groups = ForumManager.__get_all_groups()
        user_groups = set(ForumManager.__get_user_groups(userid))
        act_groups = set([g.replace(' ', '-') for g in groups])
        addgroups = act_groups - user_groups
        remgroups = user_groups - act_groups
        print username
        print addgroups
        print remgroups
        for g in addgroups:
            if not g in forum_groups:
                forum_groups[g] = ForumManager.__create_group(g)
            ForumManager.__add_user_to_group(userid, forum_groups[g])

        for g in remgroups:
            ForumManager.__remove_user_from_group(userid, forum_groups[g])

    @staticmethod
    def remove_group(username, group):
        cursor = connections['phpbb3'].cursor()
        userid = ForumManager.__get_user_id(username)
        groupid = ForumManager.__get_group_id(group)

        if userid:
            if groupid:
                cursor.execute(ForumManager.SQL_REMOVE_USER_GROUP, [userid, groupid])


    @staticmethod
    def check_user(username):
        cursor = connections['phpbb3'].cursor()
        """ Check if the username exists """
        cursor.execute(ForumManager.SQL_USER_ID_FROM_USERNAME, [ForumManager.__santatize_username(username)])
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