from rest_framework import serializers
from timerboard.models import Timer
from authapi.eveonline.serializers import EveCharacterSerializer, EveCorporationInfoSerializer
from authapi.serializers import UsernameSerializerMixin
from authapi.auth.serializers import UserSerializer

class TimerSerializer(serializers.HyperlinkedModelSerializer, UsernameSerializerMixin):
     
    class Meta:
        model = Timer
        fields = '__all__'

    def validate(self, data):
        if 'eve_character' in data and 'eve_corp' in data:
            if data['eve_character'].corporation_id != data['eve_corp'].corporation_id:
                raise serializers.ValidationError({'eve_corp': "Timer corp must be the owning character's corp.",})
        return super(TimerSerializer, self).validate(data)

class TimerExpandedSerializer(TimerSerializer):
    eve_character = EveCharacterSerializer()
    eve_corp = EveCorporationInfoSerializer()
    user = UserSerializer()
