from __future__ import unicode_literals

from django.db.models.signals import m2m_changed, pre_save
from django.contrib.auth.models import User, Group, Permission

from services.signals import m2m_changed_user_groups, pre_save_user
from services.signals import m2m_changed_group_permissions, m2m_changed_user_permissions
from authentication.signals import pre_save_auth_state

from authentication.tasks import make_member, make_blue
from authentication.models import AuthServicesInfo
from authentication.states import MEMBER_STATE, BLUE_STATE, NONE_STATE

from eveonline.models import EveCharacter


class AuthUtils:
    def __init__(self):
        pass

    @staticmethod
    def _create_user(username):
        return User.objects.create(username=username)

    @classmethod
    def create_user(cls, username, disconnect_signals=False):
        if disconnect_signals:
            cls.disconnect_signals()
        user = cls._create_user(username)
        user.authservicesinfo.state = NONE_STATE
        user.authservicesinfo.save()
        if disconnect_signals:
            cls.connect_signals()
        return user

    @classmethod
    def create_member(cls, username):
        cls.disconnect_signals()
        user = cls._create_user(username)
        user.authservicesinfo.state = MEMBER_STATE
        user.authservicesinfo.save()
        make_member(user.authservicesinfo)
        cls.connect_signals()
        return user

    @classmethod
    def create_blue(cls, username):
        cls.disconnect_signals()
        user = cls._create_user(username)
        user.authservicesinfo.state = BLUE_STATE
        user.authservicesinfo.save()
        make_blue(user.authservicesinfo)
        cls.connect_signals()
        return user

    @classmethod
    def disconnect_signals(cls):
        m2m_changed.disconnect(m2m_changed_user_groups, sender=User.groups.through)
        m2m_changed.disconnect(m2m_changed_group_permissions, sender=Group.permissions.through)
        m2m_changed.disconnect(m2m_changed_user_permissions, sender=User.user_permissions.through)
        pre_save.disconnect(pre_save_user, sender=User)
        pre_save.disconnect(pre_save_auth_state, sender=AuthServicesInfo)

    @classmethod
    def connect_signals(cls):
        m2m_changed.connect(m2m_changed_user_groups, sender=User.groups.through)
        m2m_changed.connect(m2m_changed_group_permissions, sender=Group.permissions.through)
        m2m_changed.connect(m2m_changed_user_permissions, sender=User.user_permissions.through)
        pre_save.connect(pre_save_user, sender=User)
        pre_save.connect(pre_save_auth_state, sender=AuthServicesInfo)

    @classmethod
    def add_main_character(cls, user, name, character_id, corp_id='', corp_name='', corp_ticker='', alliance_id='',
                           alliance_name=''):
        EveCharacter.objects.create(
            character_id=character_id,
            character_name=name,
            corporation_id=corp_id,
            corporation_name=corp_name,
            corporation_ticker=corp_ticker,
            alliance_id=alliance_id,
            alliance_name=alliance_name,
            api_id='1234',
            user=user
        )
        AuthServicesInfo.objects.update_or_create(user=user, defaults={'main_char_id': character_id})

    @classmethod
    def add_permissions_to_groups(cls, perms, groups, disconnect_signals=True):
        if disconnect_signals:
            cls.disconnect_signals()

        for group in groups:
            for perm in perms:
                group.permissions.add(perm)

        if disconnect_signals:
            cls.connect_signals()
