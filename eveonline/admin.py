from __future__ import unicode_literals
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from eveonline.models import EveCharacter
from eveonline.models import EveAllianceInfo
from eveonline.models import EveCorporationInfo

admin.site.register(EveAllianceInfo)
admin.site.register(EveCorporationInfo)


class EveCharacterAdmin(admin.ModelAdmin):
    search_fields = ['character_name', 'corporation_name', 'alliance_name', 'character_ownership__user__username']
    list_display = ('character_name', 'corporation_name', 'alliance_name', 'user', 'main_character')

    @staticmethod
    def user(obj):
        try:
            return obj.character_ownership.user
        except (AttributeError, ObjectDoesNotExist):
            return None

    @staticmethod
    def main_character(obj):
        try:
            return obj.character_ownership.user.profile.main_character
        except (AttributeError, ObjectDoesNotExist):
            return None


admin.site.register(EveCharacter, EveCharacterAdmin)
