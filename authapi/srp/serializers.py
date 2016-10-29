from rest_framework import serializers
from srp.models import SrpFleetMain, SrpUserRequest
from eveonline.models import EveCharacter

class SrpUserRequestSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = SrpUserRequest
        fields = "__all__"

class SrpFleetMainSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = SrpFleetMain
        fields = (
            'fleet_name',
            'fleet_doctrine',
            'fleet_time',
            'fleet_srp_code',
            'fleet_srp_status',
            'fleet_commander',
            'fleet_srp_aar_link',
            'srpuserrequest_set',
        )
        extra_kwargs = {
            'srpuserrequest_set': {'read_only': True},
        }
