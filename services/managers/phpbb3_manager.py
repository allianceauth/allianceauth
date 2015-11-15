import os
import calendar
from datetime import datetime

from passlib.apps import phpbb3_context
from django.db import connections


class Phpbb3Manager:
    SQL_ADD_USER = r"INSERT INTO phpbb_users (username, username_clean, " \
                   r"user_password, user_email, group_id, user_regdate, user_permissions, " \
                   r"user_sig) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

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

    SQL_ADD_USER_AVATAR = r"UPDATE phpbb_users SET (user_avatar_type, user_avatar_width, user_avatar_height, user_avatar) = (2,64,64,%s) WHERE user_id = %s"

    def __init__(self):
        pass

    @staticmethod
    def __add_avatar(username, characterid):
        avatar_url = "http://image.eveonline.com/Character/" + characterid + "_64.jpg"
        cursor = connections['phpbb3'].cursor()
        userid = Phpbb3Manager__get_user_id(username)
        cursor.execute(Phpbb3Manager.SQL_ADD_USER_AVATAR, [avatar_url, userid])

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def __gen_hash(password):
        return phpbb3_context.encrypt(password)

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "")
        return sanatized.lower()

    @staticmethod
    def __get_group_id(groupname):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_GET_GROUP_ID, [groupname])
        row = cursor.fetchone()

        return row[0]

    @staticmethod
    def __get_user_id(username):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_USER_ID_FROM_USERNAME, [username])
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            return None

    @staticmethod
    def __get_all_groups():
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_GET_ALL_GROUPS)
        rows = cursor.fetchall()
        out = {}
        for row in rows:
            out[row[1]] = row[0]

        return out

    @staticmethod
    def __get_user_groups(userid):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_GET_USER_GROUPS, [userid])
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def __get_current_utc_date():
        d = datetime.utcnow()
        unixtime = calendar.timegm(d.utctimetuple())
        return unixtime

    @staticmethod
    def __create_group(groupname):
        cursor = connections['phpbb3'].cursor()
        cursor.execute(Phpbb3Manager.SQL_ADD_GROUP, [groupname, groupname])
        return Phpbb3Manager.__get_group_id(groupname)

    @staticmethod
    def __add_user_to_group(userid, groupid):
        try:
            cursor = connections['phpbb3'].cursor()
            cursor.execute(Phpbb3Manager.SQL_ADD_USER_GROUP, [groupid, userid, 0])
        except:
            pass

    @staticmethod
    def __remove_user_from_group(userid, groupid):
        cursor = connections['phpbb3'].cursor()
        try:
            cursor.execute(Phpbb3Manager.SQL_REMOVE_USER_GROUP, [userid, groupid])
        except:
            pass

    @staticmethod
    def add_user(username, email, groups, characterid):
        cursor = connections['phpbb3'].cursor()

        username_clean = Phpbb3Manager.__santatize_username(username)
        password = Phpbb3Manager.__generate_random_pass()
        pwhash = Phpbb3Manager.__gen_hash(password)

        # check if the username was simply revoked
        if Phpbb3Manager.check_user(username_clean):
            Phpbb3Manager.__update_user_info(username_clean, email, pwhash)
        else:
            try:

                cursor.execute(Phpbb3Manager.SQL_ADD_USER, [username_clean, username_clean, pwhash,
                                                            email, 2, Phpbb3Manager.__get_current_utc_date(),
                                                            "", ""])
                Phpbb3Manager.update_groups(username_clean, groups)
                Phpbb3Manager.__add_avatar(username_clean, characterid)
            except:
                pass

        return username_clean, password

    @staticmethod
    def disable_user(username):
        cursor = connections['phpbb3'].cursor()

        password = Phpbb3Manager.__gen_hash(Phpbb3Manager.__generate_random_pass())
        revoke_email = "revoked@the99eve.com"
        try:
            pwhash = Phpbb3Manager.__gen_hash(password)
            cursor.execute(Phpbb3Manager.SQL_DIS_USER, [revoke_email, pwhash, username])
            return True
        except TypeError as e:
            print e
            return False

    @staticmethod
    def delete_user(username):
        cursor = connections['phpbb3'].cursor()

        if Phpbb3Manager.check_user(username):
            cursor.execute(Phpbb3Manager.SQL_DEL_USER, [username])
            return True
        return False

    @staticmethod
    def update_groups(username, groups):
        userid = Phpbb3Manager.__get_user_id(username)
        if userid is not None:
            forum_groups = Phpbb3Manager.__get_all_groups()
            user_groups = set(Phpbb3Manager.__get_user_groups(userid))
            act_groups = set([g.replace(' ', '-') for g in groups])
            addgroups = act_groups - user_groups
            remgroups = user_groups - act_groups
            print username
            print addgroups
            print remgroups
            for g in addgroups:
                if not g in forum_groups:
                    forum_groups[g] = Phpbb3Manager.__create_group(g)
                Phpbb3Manager.__add_user_to_group(userid, forum_groups[g])

            for g in remgroups:
                Phpbb3Manager.__remove_user_from_group(userid, forum_groups[g])

    @staticmethod
    def remove_group(username, group):
        cursor = connections['phpbb3'].cursor()
        userid = Phpbb3Manager.__get_user_id(username)
        if userid is not None:
            groupid = Phpbb3Manager.__get_group_id(group)

            if userid:
                if groupid:
                    try:
                        cursor.execute(Phpbb3Manager.SQL_REMOVE_USER_GROUP, [userid, groupid])
                    except:
                        pass

    @staticmethod
    def check_user(username):
        cursor = connections['phpbb3'].cursor()
        """ Check if the username exists """
        cursor.execute(Phpbb3Manager.SQL_USER_ID_FROM_USERNAME, [Phpbb3Manager.__santatize_username(username)])
        row = cursor.fetchone()
        if row:
            return True
        return False

    @staticmethod
    def update_user_password(username, characterid):
        cursor = connections['phpbb3'].cursor()
        password = Phpbb3Manager.__generate_random_pass()
        if Phpbb3Manager.check_user(username):
            pwhash = Phpbb3Manager.__gen_hash(password)
            cursor.execute(Phpbb3Manager.SQL_UPDATE_USER_PASSWORD, [pwhash, username])
            Phpbb3Manager.__add_avater(username, characterid)
            return password

        return ""

    @staticmethod
    def __update_user_info(username, email, password):
        cursor = connections['phpbb3'].cursor()
        try:
            cursor.execute(Phpbb3Manager.SQL_DIS_USER, [email, password, username])
        except:
            pass
