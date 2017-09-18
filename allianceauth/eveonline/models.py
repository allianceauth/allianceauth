from django.db import models


class EveCharacter(models.Model):
    character_id = models.CharField(max_length=254, unique=True)
    character_name = models.CharField(max_length=254, unique=True)
    corporation_id = models.CharField(max_length=254)
    corporation_name = models.CharField(max_length=254)
    corporation_ticker = models.CharField(max_length=254)
    alliance_id = models.CharField(max_length=254, blank=True, null=True, default='')
    alliance_name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        return self.character_name


class EveAllianceInfo(models.Model):
    alliance_id = models.CharField(max_length=254, unique=True)
    alliance_name = models.CharField(max_length=254, unique=True)
    alliance_ticker = models.CharField(max_length=254)
    executor_corp_id = models.CharField(max_length=254)

    def __str__(self):
        return self.alliance_name


class EveCorporationInfo(models.Model):
    corporation_id = models.CharField(max_length=254, unique=True)
    corporation_name = models.CharField(max_length=254, unique=True)
    corporation_ticker = models.CharField(max_length=254)
    member_count = models.IntegerField()
    alliance = models.ForeignKey(EveAllianceInfo, blank=True, null=True)

    def __str__(self):
        return self.corporation_name
