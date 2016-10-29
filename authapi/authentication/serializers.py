from __future__ import unicode_literals
from rest_framework import serializers
from authentication.models import AuthServicesInfo
from django.contrib.auth.models import User
from authapi.serializers import UsernameSerializerMixin

class AuthServicesInfoSerializer(serializers.ModelSerializer, UsernameSerializerMixin):

    class Meta:
        model = AuthServicesInfo
        fields = (
            'user',
            'state',
            'main_char_id',
            'ipboard_username',
            'xenforo_username',
            'forum_username',
            'jabber_username',
            'mumble_username',
            'teamspeak3_uid',
            'teamspeak3_perm_key',
            'discord_uid',
            'discourse_enabled',
            'ips4_username',
            'ips4_id',
            'smf_username',
            'market_username',
        )
