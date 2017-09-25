from django.db import models

from .managers import EveCharacterManager, EveCharacterProviderManager
from .managers import EveCorporationManager, EveCorporationProviderManager
from .managers import EveAllianceManager, EveAllianceProviderManager
from . import providers


class EveCharacter(models.Model):
    character_id = models.CharField(max_length=254, unique=True)
    character_name = models.CharField(max_length=254, unique=True)
    corporation_id = models.CharField(max_length=254)
    corporation_name = models.CharField(max_length=254)
    corporation_ticker = models.CharField(max_length=254)
    alliance_id = models.CharField(max_length=254, blank=True, null=True, default='')
    alliance_name = models.CharField(max_length=254, blank=True, null=True, default='')

    objects = EveCharacterManager()
    provider = EveCharacterProviderManager()

    def update_character(self, character: providers.Character = None):
        if character is None:
            character = self.provider.get_character(self.character_id)
        self.character_name = character.name
        self.corporation_id = character.corp.id
        self.corporation_name = character.corp.name
        self.corporation_ticker = character.corp.ticker
        self.alliance_id = character.alliance.id
        self.alliance_name = character.alliance.name
        self.save()
        return self

    def __str__(self):
        return self.character_name


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


class EveCorporationInfo(models.Model):
    corporation_id = models.CharField(max_length=254, unique=True)
    corporation_name = models.CharField(max_length=254, unique=True)
    corporation_ticker = models.CharField(max_length=254)
    member_count = models.IntegerField()
    alliance = models.ForeignKey(EveAllianceInfo, blank=True, null=True)

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
