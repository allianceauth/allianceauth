from django.contrib import admin

from models import EveCharacter
from models import EveApiKeyPair
from models import EveAllianceInfo
from models import EveCorporationInfo

admin.site.register(EveCharacter)
admin.site.register(EveApiKeyPair)
admin.site.register(EveAllianceInfo)
admin.site.register(EveCorporationInfo)