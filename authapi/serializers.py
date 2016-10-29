from __future__ import unicode_literals
from rest_framework import serializers
from django.contrib.auth.models import User

class UsernameSerializerMixin:
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
    )

class UsernameHyperlinkSerializerMixin:
    user = serializers.HyperlinkedRelatedField(
        queryset = User.objects.all(),
        view_name = 'user-detail',
        lookup_field = 'username',
    )


def GenericSerializer(for_model, field_list='__all__', model_lookup_field='pk'):
    class GenericModelSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = for_model
            fields = field_list
            lookup_field=model_lookup_field

    return GenericModelSerializer
