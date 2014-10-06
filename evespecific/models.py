from django.db import models

from authentication.models import AllianceUser


class EveCharacter(models.Model):
    character_id = models.CharField(max_length=254)
    character_name = models.CharField(max_length=254)
    corporation_id = models.CharField(max_length=254)
    corporation_name = models.CharField(max_length=254)
    corporation_ticker = models.CharField(max_length=254)
    alliance_id = models.CharField(max_length=254)
    alliance_name = models.CharField(max_length=254)
    api_id = models.CharField(max_length=254)
    user = models.ForeignKey(AllianceUser)


class EveApiKeyPair(models.Model):
    api_id = models.CharField(max_length=254)
    api_key = models.CharField(max_length=254)
    user = models.ForeignKey(AllianceUser)