from django.contrib.auth.models import User

from models import AuthServicesInfo


class AuthServicesInfoManager:
    def __init__(self):
        pass

    @staticmethod
    def __get_or_create(user):
        if AuthServicesInfo.objects.filter(user=user).exists():
            return AuthServicesInfo.objects.get(user=user)
        else:
            # We have to create
            print 'here'
            authserviceinfo = AuthServicesInfo()
            authserviceinfo.user = user
            authserviceinfo.save()
            return authserviceinfo

    @staticmethod
    def get_auth_service_info(user):
        if User.objects.filter(username=user.username).exists():
            return AuthServicesInfoManager.__get_or_create(user)
        return None

    @staticmethod
    def update_main_char_Id(char_id, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.main_char_id = char_id
            authserviceinfo.save(update_fields=['main_char_id'])

    @staticmethod
    def update_user_forum_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.forum_username = username
            authserviceinfo.forum_password = password
            authserviceinfo.save(update_fields=['forum_username', 'forum_password'])

    @staticmethod
    def update_user_jabber_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.jabber_username = username
            authserviceinfo.jabber_password = password
            authserviceinfo.save(update_fields=['jabber_username', 'jabber_password'])


    @staticmethod
    def update_user_mumble_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.mumble_username = username
            authserviceinfo.mumble_password = password
            authserviceinfo.save(update_fields=['mumble_username', 'mumble_password'])

    @staticmethod
    def update_user_ipboard_info(username, password, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.ipboard_username = username
            authserviceinfo.ipboard_password = password
            authserviceinfo.save(update_fields=['ipboard_username', 'ipboard_password'])

    @staticmethod
    def update_user_teamspeak3_info(uid, perm_key, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.teamspeak3_uid = uid
            authserviceinfo.teamspeak3_perm_key = perm_key
            authserviceinfo.save(update_fields=['teamspeak3_uid', 'teamspeak3_perm_key'])

    @staticmethod
    def update_is_blue(is_blue, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.is_blue = is_blue
            authserviceinfo.save(update_fields=['is_blue'])

    @staticmethod
    def update_user_discord_info(user_id, user):
        if User.objects.filter(username=user.username).exists():
            authserviceinfo = AuthServicesInfoManager.__get_or_create(user)
            authserviceinfo.discord_uid = user_id
            authserviceinfo.save(update_fields=['discord_uid'])
