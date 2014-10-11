import os
import hashlib
from django.db import connections
from django.conf import settings


class MumbleManager:

    SQL_SELECT_USER_MAX_ID = r"SELECT max(user_id)+1 as next_id from murmur_users"

    SQL_SELECT_GROUP_MAX_ID = r"SELECT MAX(group_id)+1 FROM murmur_groups"

    SQL_CREATE_USER = r"INSERT INTO murmur_users (server_id, user_id, name, pw) VALUES (%s, %s, %s, %s)"

    SQL_SELECT_GET_USER_ID_BY_NAME = r"SELECT user_id from murmur_users WHERE name = %s AND server_id = %s"

    SQL_CHECK_USER_EXIST = r"SELECT name from murmur_users WHERE name = %s AND server_id = %s"

    SQL_DELETE_USER = r"DELETE FROM murmur_users WHERE name = %s AND server_id = %s"

    SQL_UPDATE_USER_PASSWORD = r"UPDATE murmur_users SET pw = %s WHERE name = %s AND server_id = %s"

    SQL_GET_GROUPS = r"SELECT group_id, name FROM murmur_groups WHERE server_id = %s AND channel_id = 0"

    SQL_GET_GROUP_FROM_NAME = r"SELECT group_id, name FROM murmur_groups " \
                              r"WHERE server_id = %s AND channel_id = 0 AND name = %s"

    SQL_GET_USER_GROUPS = r"SELECT murmur_groups.name FROM murmur_groups, murmur_group_members WHERE " \
                          r"murmur_group_members.group_id = murmur_groups.group_id AND " \
                          r"murmur_group_members.server_id = murmur_groups.server_id AND " \
                          r"murmur_group_members.user_id = %s"

    SQL_ADD_GROUP = r"INSERT INTO murmur_groups (group_id, server_id, name, channel_id, inherit, inheritable) " \
                    r"VALUES (%s, %s, %s, 0, 1, 1)"

    SQL_ADD_USER_TO_GROUP = r"INSERT INTO murmur_group_members (group_id, server_id, user_id, addit) " \
                            r"VALUES (%s, %s, %s, 1)"

    SQL_DELETE_USER_FROM_GROUP = r"DELETE FROM murmur_group_members WHERE group_id = %s " \
                                 r"AND server_id = %s AND user_id = %s"

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
    def _get_groups():
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_GET_GROUPS, [settings.MUMBLE_SERVER_ID])
        rows = dbcursor.fetchall()

        out = {}
        for row in rows:
            out[row[1]] = row[0]

        return out

    @staticmethod
    def _get_group(name):
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_GET_GROUP_FROM_NAME, [settings.MUMBLE_SERVER_ID, name])
        row = dbcursor.fetchone()
        if row:
            return row[0]

    @staticmethod
    def _get_user_groups(name):
        dbcursor = connections['mumble'].cursor()
        user_id = MumbleManager.get_user_id_by_name(name)
        dbcursor.execute(MumbleManager.SQL_GET_USER_GROUPS, [user_id])
        return [row[0] for row in dbcursor.fetchall()]

    @staticmethod
    def _add_group(name):
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_SELECT_GROUP_MAX_ID)
        row = dbcursor.fetchone()
        groupid = row[0]
        dbcursor.execute(MumbleManager.SQL_ADD_GROUP, [groupid, settings.MUMBLE_SERVER_ID, name])
        return groupid

    @staticmethod
    def _add_user_to_group(userid, groupid):
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_ADD_USER_TO_GROUP, [groupid, settings.MUMBLE_SERVER_ID, userid])

    @staticmethod
    def _del_user_from_group(userid, groupid):
        dbcursor = connections['mumble'].cursor()
        dbcursor.execute(MumbleManager.SQL_DELETE_USER_FROM_GROUP, [groupid, settings.MUMBLE_SERVER_ID, userid])

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
            dbcursor.execute(MumbleManager.SQL_SELECT_USER_MAX_ID)
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

    @staticmethod
    def update_groups(username, groups):
        userid = MumbleManager.get_user_id_by_name(username)
        mumble_groups = MumbleManager._get_groups()
        user_groups = set(MumbleManager._get_user_groups(username))
        act_groups = set([g.replace(' ', '-') for g in groups])
        addgroups = act_groups - user_groups
        remgroups = user_groups - act_groups

        for g in addgroups:
            if not g in mumble_groups:
                mumble_groups[g] = MumbleManager._add_group(g)
            MumbleManager._add_user_to_group(userid, mumble_groups[g])

        for g in remgroups:
            MumbleManager._del_user_from_group(userid, mumble_groups[g])
