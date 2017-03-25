from __future__ import unicode_literals
from eveonline.models import EveCharacter
from eveonline.models import EveAllianceInfo
from eveonline.models import EveCorporationInfo
from eveonline.providers import eve_adapter_factory
import logging

logger = logging.getLogger(__name__)


class EveManager(object):
    adapter = None

    @classmethod
    def get_adapter(cls):
        if not cls.adapter:
            cls.adapter = eve_adapter_factory()
        return cls.adapter

    @classmethod
    def get_character(cls, character_id):
        return cls.get_adapter().get_character(character_id)

    @staticmethod
    def create_character(id):
        return EveManager.create_character_obj(EveManager.get_character(id))

    @staticmethod
    def create_character_obj(character,):
        return EveCharacter.objects.create(
            character_id=character.id,
            character_name=character.name,
            corporation_id=character.corp.id,
            corporation_name=character.corp.name,
            corporation_ticker=character.corp.ticker,
            alliance_id=character.alliance.id,
            alliance_name=character.alliance.name,
        )

    @staticmethod
    def update_character(id):
        return EveManager.update_character_obj(EveManager.get_character(id))

    @staticmethod
    def update_character_obj(char):
        model = EveCharacter.objects.get(character_id=char.id)
        model.character_name = char.name
        model.corporation_id = char.corp.id
        model.corporation_name = char.corp.name
        model.corporation_ticker = char.corp.ticker
        model.alliance_id = char.alliance.id
        model.alliance_name = char.alliance.name
        model.save()
        return model

    @classmethod
    def get_alliance(cls, alliance_id):
        return cls.get_adapter().get_alliance(alliance_id)

    @staticmethod
    def create_alliance(id):
        return EveManager.create_alliance_obj(EveManager.get_alliance(id))

    @staticmethod
    def create_alliance_obj(alliance):
        return EveAllianceInfo.objects.create(
            alliance_id=alliance.id,
            alliance_name=alliance.name,
            alliance_ticker=alliance.ticker,
            executor_corp_id=alliance.executor_corp_id,
        )

    @staticmethod
    def update_alliance(id):
        return EveManager.update_alliance_obj(EveManager.get_alliance(id))

    @staticmethod
    def update_alliance_obj(alliance):
        model = EveAllianceInfo.objects.get(alliance_id=alliance.id)
        model.executor_corp_id = alliance.executor_corp_id
        model.save()
        return model

    @staticmethod
    def populate_alliance(id):
        alliance_model = EveAllianceInfo.objects.get(alliance_id=id)
        alliance = EveManager.get_alliance(id)
        for corp_id in alliance.corp_ids:
            if not EveCorporationInfo.objects.filter(corporation_id=corp_id).exists():
                EveManager.create_corporation(corp_id)
        EveCorporationInfo.objects.filter(corporation_id__in=alliance.corp_ids).update(alliance=alliance_model)
        EveCorporationInfo.objects.filter(alliance=alliance_model).exclude(corporation_id__in=alliance.corp_ids).update(
            alliance=None)

    @classmethod
    def get_corporation(cls, corp_id):
        return cls.get_adapter().get_corp(corp_id)

    @staticmethod
    def create_corporation(id):
        return EveManager.create_corporation_obj(EveManager.get_corporation(id))

    @staticmethod
    def create_corporation_obj(corp):
        try:
            alliance = EveAllianceInfo.objects.get(alliance_id=corp.alliance_id)
        except EveAllianceInfo.DoesNotExist:
            alliance = None
        return EveCorporationInfo.objects.create(
            corporation_id=corp.id,
            corporation_name=corp.name,
            corporation_ticker=corp.ticker,
            member_count=corp.members,
            alliance=alliance,
        )

    @staticmethod
    def update_corporation(id):
        return EveManager.update_corporation_obj(EveManager.get_corporation(id))

    @staticmethod
    def update_corporation_obj(corp):
        model = EveCorporationInfo.objects.get(corporation_id=corp.id)
        model.member_count = corp.members
        try:
            model.alliance = EveAllianceInfo.objects.get(alliance_id=corp.alliance_id)
        except EveAllianceInfo.DoesNotExist:
            model.alliance = None
        model.save()
        return model

    @classmethod
    def get_itemtype(cls, type_id):
        return cls.get_adapter().get_itemtype(type_id)

    @staticmethod
    def check_if_character_exist(char_name):
        return EveCharacter.objects.filter(character_name=char_name).exists()

    @staticmethod
    def get_characters_by_owner_id(user):
        if EveCharacter.objects.filter(user=user).exists():
            return EveCharacter.objects.all().filter(user=user)

        return None

    @staticmethod
    def get_character_by_character_name(char_name):
        if EveCharacter.objects.filter(character_name=char_name).exists():
            return EveCharacter.objects.get(character_name=char_name)

    @staticmethod
    def get_character_by_id(char_id):
        if EveCharacter.objects.filter(character_id=char_id).exists():
            return EveCharacter.objects.get(character_id=char_id)

        return None

    @staticmethod
    def get_characters_by_api_id(api_id):
        return EveCharacter.objects.filter(api_id=api_id)

    @staticmethod
    def get_charater_alliance_id_by_id(char_id):
        if EveCharacter.objects.filter(character_id=char_id).exists():
            return EveCharacter.objects.get(character_id=char_id).alliance_id

    @staticmethod
    def check_if_character_owned_by_user(char_id, user):
        character = EveCharacter.objects.get(character_id=char_id)

        if character.user.id == user.id:
            return True

        return False

    @staticmethod
    def check_if_alliance_exists_by_id(alliance_id):
        return EveAllianceInfo.objects.filter(alliance_id=alliance_id).exists()

    @staticmethod
    def check_if_corporation_exists_by_id(corp_id):
        return EveCorporationInfo.objects.filter(corporation_id=corp_id).exists()

    @staticmethod
    def get_alliance_info_by_id(alliance_id):
        if EveManager.check_if_alliance_exists_by_id(alliance_id):
            return EveAllianceInfo.objects.get(alliance_id=alliance_id)
        else:
            return None

    @staticmethod
    def get_corporation_info_by_id(corp_id):
        if EveManager.check_if_corporation_exists_by_id(corp_id):
            return EveCorporationInfo.objects.get(corporation_id=corp_id)
        else:
            return None

    @staticmethod
    def get_all_corporation_info():
        return EveCorporationInfo.objects.all()

    @staticmethod
    def get_all_alliance_info():
        return EveAllianceInfo.objects.all()

    @staticmethod
    def get_charater_corporation_id_by_id(char_id):
        if EveCharacter.objects.filter(character_id=char_id).exists():
            return EveCharacter.objects.get(character_id=char_id).corporation_id
