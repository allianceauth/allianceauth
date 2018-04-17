from django.db import models
from typing import Union

from .managers import EveCharacterManager, EveCharacterProviderManager
from .managers import EveCorporationManager, EveCorporationProviderManager
from .managers import EveAllianceManager, EveAllianceProviderManager
from . import providers


class EveAllianceInfo(models.Model):
    alliance_id = models.CharField(max_length=254, unique=True)
    alliance_name = models.CharField(max_length=254, unique=True)
    alliance_ticker = models.CharField(max_length=254)
    executor_corp_id = models.CharField(max_length=254)

    objects = EveAllianceManager()
    provider = EveAllianceProviderManager()

    def populate_alliance(self):
        alliance = self.provider.get_alliance(self.alliance_id)
        for corp_id in alliance.corp_ids:
            if not EveCorporationInfo.objects.filter(corporation_id=corp_id).exists():
                EveCorporationInfo.objects.create_corporation(corp_id)
        EveCorporationInfo.objects.filter(corporation_id__in=alliance.corp_ids).update(alliance=self)
        EveCorporationInfo.objects.filter(alliance=self).exclude(corporation_id__in=alliance.corp_ids).update(
            alliance=None)

    def update_alliance(self, alliance: providers.Alliance = None):
        if alliance is None:
            alliance = self.provider.get_alliance(self.alliance_id)
        self.executor_corp_id = alliance.executor_corp_id
        self.save()
        return self

    def __str__(self):
        return self.alliance_name

    def logo_url(self, size=32):
        return "https://image.eveonline.com/Alliance/%s_%s.png" % (self.alliance_id, size)

    def __getattr__(self, item):
        if item.startswith('logo_url_'):
            size = item.strip('logo_url_')
            return self.logo_url(size)
        return self.__getattribute__(item)


class EveCorporationInfo(models.Model):
    corporation_id = models.CharField(max_length=254, unique=True)
    corporation_name = models.CharField(max_length=254, unique=True)
    corporation_ticker = models.CharField(max_length=254)
    member_count = models.IntegerField()
    alliance = models.ForeignKey(EveAllianceInfo, blank=True, null=True, on_delete=models.SET_NULL)

    objects = EveCorporationManager()
    provider = EveCorporationProviderManager()

    def update_corporation(self, corp: providers.Corporation = None):
        if corp is None:
            corp = self.provider.get_corporation(self.corporation_id)
        self.member_count = corp.members
        try:
            self.alliance = EveAllianceInfo.objects.get(alliance_id=corp.alliance_id)
        except EveAllianceInfo.DoesNotExist:
            self.alliance = None
        self.save()
        return self

    def __str__(self):
        return self.corporation_name

    def logo_url(self, size=32):
        return "https://image.eveonline.com/Corporation/%s_%s.png" % (self.corporation_id, size)

    def __getattr__(self, item):
        if item.startswith('logo_url_'):
            size = item.strip('logo_url_')
            return self.logo_url(size)
        return self.__getattribute__(item)


class EveCharacter(models.Model):
    character_id = models.CharField(max_length=254, unique=True)
    character_name = models.CharField(max_length=254, unique=True)
    corporation_id = models.CharField(max_length=254)
    corporation_name = models.CharField(max_length=254)
    corporation_ticker = models.CharField(max_length=5)
    alliance_id = models.CharField(max_length=254, blank=True, null=True, default='')
    alliance_name = models.CharField(max_length=254, blank=True, null=True, default='')
    alliance_ticker = models.CharField(max_length=5, blank=True, null=True, default='')

    objects = EveCharacterManager()
    provider = EveCharacterProviderManager()

    @property
    def alliance(self) -> Union[EveAllianceInfo, None]:
        """
        Pseudo foreign key from alliance_id to EveAllianceInfo
        :raises: EveAllianceInfo.DoesNotExist
        :return: EveAllianceInfo or None
        """
        if self.alliance_id is None:
            return None
        return EveAllianceInfo.objects.get(alliance_id=self.alliance_id)

    @property
    def corporation(self) -> EveCorporationInfo:
        """
        Pseudo foreign key from corporation_id to EveCorporationInfo
        :raises: EveCorporationInfo.DoesNotExist
        :return: EveCorporationInfo
        """
        return EveCorporationInfo.objects.get(corporation_id=self.corporation_id)

    def update_character(self, character: providers.Character = None):
        if character is None:
            character = self.provider.get_character(self.character_id)
        self.character_name = character.name
        self.corporation_id = character.corp.id
        self.corporation_name = character.corp.name
        self.corporation_ticker = character.corp.ticker
        self.alliance_id = character.alliance.id
        self.alliance_name = character.alliance.name
        self.alliance_ticker = getattr(character.alliance, 'ticker', None)
        self.save()
        return self

    def __str__(self):
        return self.character_name

    def portrait_url(self, size=32):
        return "https://image.eveonline.com/Character/%s_%s.jpg" % (self.character_id, size)

    def __getattr__(self, item):
        if item.startswith('portrait_url_'):
            size = item.strip('portrait_url_')
            return self.portrait_url(size)
        return self.__getattribute__(item)
