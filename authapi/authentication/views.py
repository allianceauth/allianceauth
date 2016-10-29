from rest_framework import generics
from authentication.models import AuthServicesInfo
from authapi.authentication.serializers import AuthServicesInfoSerializer


class AuthServicesInfoList(generics.ListCreateAPIView):
    queryset = AuthServicesInfo.objects.all()
    serializer_class = AuthServicesInfoSerializer


class AuthServicesInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AuthServicesInfo.objects.all()
    serializer_class = AuthServicesInfoSerializer
