from eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo, EveApiKeyPair
from authapi.auth.serializers import UserSerializer
from authapi.serializers import GenericSerializer, UsernameHyperlinkSerializerMixin

EveCharacterSerializer = GenericSerializer(EveCharacter)
EveCorporationInfoSerializer = GenericSerializer(EveCorporationInfo)
EveAllianceInfoSerializer = GenericSerializer(EveAllianceInfo)
EveApiKeyPairSerializer = GenericSerializer(EveApiKeyPair)

class EveCharacterExpandedSerializer(EveCharacterSerializer):
    user = UserSerializer()

class EveApiKeyPairExpandedSerializer(EveApiKeyPairSerializer):
    user = UserSerializer()
