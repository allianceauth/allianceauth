from django.contrib import admin

from models import EveCharacter
from models import EveApiKeyPair
from models import EveAllianceInfo
from models import EveCorporationInfo

admin.site.register(EveApiKeyPair)
admin.site.register(EveAllianceInfo)
admin.site.register(EveCorporationInfo)


class EveCharacterAdmin(admin.ModelAdmin):
  search_fields = ['character_name', 'corporation_name', 'alliance_name', 'user__username']
  list_display = ('character_name', 'corporation_name', 'alliance_name', 'user')

admin.site.register(EveCharacter, EveCharacterAdmin)
