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
    list_display = ['api_id', 'user', 'characters']

    @staticmethod
    def characters(obj):
        return ', '.join(sorted([c.character_name for c in EveCharacter.objects.filter(api_id=obj.api_id)]))

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(EveApiKeyPairAdmin, self).get_search_results(request, queryset, search_term)
        chars = EveCharacter.objects.filter(character_name__icontains=search_term)
        queryset |= EveApiKeyPair.objects.filter(api_id__in=[char.api_id for char in chars if bool(char.api_id)])
        return queryset, use_distinct


class EveCharacterAdmin(admin.ModelAdmin):
    search_fields = ['character_name', 'corporation_name', 'alliance_name', 'user__username', 'api_id']
    list_display = ('character_name', 'corporation_name', 'alliance_name', 'user', 'main_character')

    @staticmethod
    def main_character(obj):
        if obj.user:
            auth = AuthServicesInfo.objects.get(user=obj.user)
            if auth and auth.main_char_id:
                try:
                    return EveCharacter.objects.get(character_id=auth.main_char_id)
                except EveCharacter.DoesNotExist:
                    pass
        return None


admin.site.register(EveCharacter, EveCharacterAdmin)
admin.site.register(EveApiKeyPair, EveApiKeyPairAdmin)
