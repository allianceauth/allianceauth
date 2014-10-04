from django.db import models

from authentication.models import AllianceUser

# Create your models here.
class EveCharacter(models.Model):
    character_id       = models.CharField(max_length=254)
    character_name     = models.CharField(max_length=254)
    corporation_id     = models.CharField(max_length=254)
    corporation_name   = models.CharField(max_length=254)
    alliance_id        = models.CharField(max_length=254)
    alliance_name      = models.CharField(max_length=254)
    allianceuser_owner = models.ForeignKey(AllianceUser)