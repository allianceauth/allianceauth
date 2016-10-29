from rest_framework import serializers
from optimer.models import optimer
from eveonline.models import EveCharacter
from authapi.eveonline.serializers import EveCharacterSerializer

class optimerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = optimer
        fields = '__all__'


    def validate(self, data):
        if 'start' in data and 'post_time' in data:
            if data['start'] < data['post_time']:
                raise serializers.ValidationError({'start': "Cannot start before posting.",})
        return super(optimerSerializer, self).validate(data)


class optimerExpandedSerializer(optimerSerializer):
    eve_character = EveCharacterSerializer()
