from django.contrib import admin

from models import EveCharacter
from models import EveApiKeyPair
from models import EveAllianceInfo
from models import EveCorporationInfo
from authentication.managers import AuthServicesInfoManager

admin.site.register(EveAllianceInfo)
admin.site.register(EveCorporationInfo)

class EveApiKeyPairAdmin(admin.ModelAdmin):
    search_fields = ['api_id', 'user__username']
    list_display = ['api_id', 'user']

class EveCharacterAdmin(admin.ModelAdmin):
    search_fields = ['character_name', 'corporation_name', 'alliance_name', 'user__username', 'api_id']
    list_display = ('character_name', 'corporation_name', 'alliance_name', 'user', 'main_character')

    def main_character(self, obj):
        auth = AuthServicesInfoManager.get_auth_service_info(obj.user)
        if auth and auth.main_char_id:
            try:
                return EveCharacter.objects.get(character_id=auth.main_char_id)
            except EveCharacter.DoesNotExist:
                pass
        return None

admin.site.register(EveCharacter, EveCharacterAdmin)
admin.site.register(EveApiKeyPair, EveApiKeyPairAdmin)
