from __future__ import unicode_literals
from django.contrib import admin

from eveonline.models import EveCharacter
from eveonline.models import EveApiKeyPair
from eveonline.models import EveAllianceInfo
from eveonline.models import EveCorporationInfo
from authentication.models import AuthServicesInfo

admin.site.register(EveAllianceInfo)
admin.site.register(EveCorporationInfo)


class EveApiKeyPairAdmin(admin.ModelAdmin):
    search_fields = ['api_id', 'user__username']
    list_display = ['api_id', 'user']


class EveCharacterAdmin(admin.ModelAdmin):
    search_fields = ['character_name', 'corporation_name', 'alliance_name', 'user__username', 'api_id']
    list_display = ('character_name', 'corporation_name', 'alliance_name', 'user', 'main_character')

    @staticmethod
    def main_character(obj):
        auth = AuthServicesInfo.objects.get_or_create(user=obj.user)[0]
        if auth and auth.main_char_id:
            try:
                return EveCharacter.objects.get(character_id=auth.main_char_id)
            except EveCharacter.DoesNotExist:
                pass
        return None


admin.site.register(EveCharacter, EveCharacterAdmin)
admin.site.register(EveApiKeyPair, EveApiKeyPairAdmin)
