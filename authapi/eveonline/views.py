from eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo, EveApiKeyPair
from authapi.eveonline.serializers import EveCharacterSerializer, EveCharacterExpandedSerializer, EveApiKeyPairExpandedSerializer
from authapi.views import GenericModelViewSet

EveCharacterViewSet = GenericModelViewSet(EveCharacter, serializers={'default': EveCharacterSerializer, 'retrieve': EveCharacterExpandedSerializer})
EveCorporationInfoViewSet = GenericModelViewSet(EveCorporationInfo)
EveAllianceInfoViewSet = GenericModelViewSet(EveAllianceInfo)
EveApiKeyPairViewSet = GenericModelViewSet(EveApiKeyPair, serializers={'retrieve': EveApiKeyPairExpandedSerializer})
