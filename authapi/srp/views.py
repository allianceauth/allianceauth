from authapi.srp.serializers import SrpUserRequestSerializer
from authapi.views import GenericModelViewSet
from srp.models import SrpFleetMain, SrpUserRequest

SrpFleetMainViewSet = GenericModelViewSet(SrpFleetMain)
SrpUserRequestViewSet = GenericModelViewSet(SrpUserRequest, serializers={'default':SrpUserRequestSerializer})
