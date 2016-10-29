from django.contrib.auth.models import User, Permission
from authapi.auth.models import Group
from authapi.views import GenericModelViewSet
from authapi.auth.serializers import UserSerializer, UserExpandedSerializer, UserCreateSerializer, GroupSerializer, GroupExpandedSerializer

PermissionViewSet = GenericModelViewSet(Permission)
UserViewSet = GenericModelViewSet(User, serializers={'default':UserSerializer, 'retrieve':UserExpandedSerializer, 'create':UserCreateSerializer, 'update':UserCreateSerializer})
GroupViewSet = GenericModelViewSet(Group, serializers={'default':GroupSerializer, 'retrieve':GroupExpandedSerializer})
