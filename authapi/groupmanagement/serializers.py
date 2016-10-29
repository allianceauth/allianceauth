from authapi.serializers import GenericSerializer
from groupmanagement.models import GroupRequest
from authapi.auth.serializers import UserSerializer
from rest_framework import serializers

class GroupRequestSerializer(GenericSerializer(GroupRequest)):
    class Meta:
        model = GroupRequest
        fields = ('__all__')
        extra_kwargs = {
            'status': {'read_only': True},
        }

    def validate(self, data):
        if data['leave_request'] and not data['group'] in data['user'].groups.all():
            raise serializers.ValidationError("Cannot leave a group without being a member first.")
        elif not data['leave_request'] and data['group'] in data['user'].groups.all():
            raise serializers.ValidationError("Cannot join a group while already being a member.")
        return data


class GroupRequestExpandedSerializer(GroupRequestSerializer):
    user = UserSerializer()
