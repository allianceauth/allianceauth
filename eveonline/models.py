from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class EveCharacter(models.Model):
    character_id = models.CharField(max_length=254)
    character_name = models.CharField(max_length=254)
    corporation_id = models.CharField(max_length=254)
    corporation_name = models.CharField(max_length=254)
    corporation_ticker = models.CharField(max_length=254)
    alliance_id = models.CharField(max_length=254)
    alliance_name = models.CharField(max_length=254)
    api_id = models.CharField(max_length=254)
    user = models.ForeignKey(User)


class EveApiKeyPair(models.Model):
    api_id = models.CharField(max_length=254)
    api_key = models.CharField(max_length=254)
    user = models.ForeignKey(User)

admin.site.register(EveCharacter)
admin.site.register(EveApiKeyPair)