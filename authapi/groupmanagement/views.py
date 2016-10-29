from rest_framework.decorators import detail_route
from authapi.views import GenericModelViewSet
from groupmanagement.models import GroupRequest
from rest_framework.response import Response
from authapi.groupmanagement.serializers import GroupRequestSerializer, GroupRequestExpandedSerializer

class GroupRequestViewSet(GenericModelViewSet(GroupRequest, serializers={'default':GroupRequestSerializer, 'retrieve':GroupRequestExpandedSerializer})):
    @detail_route(methods=['put'])
    def accept(self, request, pk=None):
        group_request = self.get_object()
        group_request.accept()
        return Response({'status': 'accepted'})

    @detail_route(methods=['put'])
    def reject(self, request, pk=None):
        group_request = self.get_object()
        group_request.reject()
        return Response({'status': 'rejected'})
