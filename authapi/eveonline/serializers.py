from eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo, EveApiKeyPair
from authapi.auth.serializers import UserSerializer
from authapi.serializers import GenericSerializer, UsernameHyperlinkSerializerMixin

class EveCharacterSerializer(GenericSerializer(EveCharacter)):
    pass


class EveCorporationInfoSerializer(GenericSerializer(EveCorporationInfo)):
    pass


class EveAllianceInfoSerializer(GenericSerializer(EveAllianceInfo)):
    pass


class EveApiKeyPairSerializer(GenericSerializer(EveApiKeyPair)):
    pass


class EveCharacterExpandedSerializer(EveCharacterSerializer):
    user = UserSerializer()


class EveApiKeyPairExpandedSerializer(EveApiKeyPairSerializer):
    user = UserSerializer()
