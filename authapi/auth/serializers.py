from rest_framework import serializers
from django.contrib.auth.models import User
from authapi.auth.models import Group

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'href',
            'username',
            'email',
            'is_active',
        )


class UserExpandedSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('__all__')
        extra_kwargs = {
            'password': {'write_only': True},
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True},
        }


class UserCreateSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'href',
            'username',
            'email',
            'password',
            'is_active',
            'is_staff',
            'is_superuser',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    hidden = serializers.BooleanField()
    open = serializers.BooleanField()
    description = serializers.CharField(max_length=254, allow_blank=True)
   
    class Meta:
        model = Group
        fields = (
            'href',
            'name',
            'description',
            'hidden',
            'open',
        )

    def create(self, validated_data, *args, **kwargs):
        hidden = validated_data.pop('hidden', False)
        open = validated_data.pop('open', False)
        description = validated_data.pop('description', '')
        instance = super(GroupSerializer, self).create(validated_data, *args, **kwargs)
        instance.hidden = hidden
        instance.open = open
        instance.description = description
        return instance

    def update(self, instance, validated_data, *args, **kwargs):
        hidden = validated_data.pop('hidden', getattr(instance, 'hidden', False))
        open = validated_data.pop('open', getattr(instance, 'open', False))
        description = validated_data.pop('description', getattr(instance, 'description', ''))
        instance = super(GroupSerializer, self).update(instance, validated_data, *args, **kwargs)
        instance.hidden = hidden
        instance.open = open
        instance.description = description
        return instance

class GroupExpandedSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = (
            'href',
            'name',
            'description',
            'hidden',
            'open',
            'grouprequest_set',
            'permissions',
        )

