import logging

from django.db import models
from . import providers

logger = logging.getLogger(__name__)


class EveCharacterProviderManager:
    def get_character(self, character_id) -> providers.Character:
        return providers.provider.get_character(character_id)


class EveCharacterManager(models.Manager):
    provider = EveCharacterProviderManager()

    def create_character(self, character_id):
        return self.create_character_obj(self.provider.get_character(character_id))

    def create_character_obj(self, character: providers.Character):
        return self.create(
            character_id=character.id,
            character_name=character.name,
            corporation_id=character.corp.id,
            corporation_name=character.corp.name,
            corporation_ticker=character.corp.ticker,
            alliance_id=character.alliance.id,
            alliance_name=character.alliance.name,
            alliance_ticker=getattr(character.alliance, 'ticker', None),
        )

    def update_character(self, character_id):
        return self.get(character_id=character_id).update_character()

    def get_character_by_id(self, char_id):
        if self.filter(character_id=char_id).exists():
            return self.get(character_id=char_id)
        return None


class EveAllianceProviderManager:
    def get_alliance(self, alliance_id) -> providers.Alliance:
        return providers.provider.get_alliance(alliance_id)


class EveAllianceManager(models.Manager):
    provider = EveAllianceProviderManager()

    def create_alliance(self, alliance_id):
        obj = self.create_alliance_obj(self.provider.get_alliance(alliance_id))
        obj.populate_alliance()
        return obj

    def create_alliance_obj(self, alliance: providers.Alliance):
        return self.create(
            alliance_id=alliance.id,
            alliance_name=alliance.name,
            alliance_ticker=alliance.ticker,
            executor_corp_id=alliance.executor_corp_id,
        )

    def update_alliance(self, alliance_id):
        return self.get(alliance_id=alliance_id).update_alliance()


class EveCorporationProviderManager:
    def get_corporation(self, corp_id) -> providers.Corporation:
        return providers.provider.get_corp(corp_id)


class EveCorporationManager(models.Manager):
    provider = EveCorporationProviderManager()

    def create_corporation(self, corp_id):
        return self.create_corporation_obj(self.provider.get_corporation(corp_id))

    def create_corporation_obj(self, corp: providers.Corporation):
        from .models import EveAllianceInfo
        try:
            alliance = EveAllianceInfo.objects.get(alliance_id=corp.alliance_id)
        except EveAllianceInfo.DoesNotExist:
            alliance = None
        return self.create(
            corporation_id=corp.id,
            corporation_name=corp.name,
            corporation_ticker=corp.ticker,
            member_count=corp.members,
            alliance=alliance,
        )

    def update_corporation(self, corp_id):
        return self.get(corporation_id=corp_id).update_corporation(self.provider.get_corporation(corp_id))
