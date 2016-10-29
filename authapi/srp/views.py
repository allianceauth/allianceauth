from authapi.srp.serializers import SrpFleetMainSerializer, SrpUserRequestSerializer
from authapi.views import GenericList, GenericModel
from srp.models import SrpFleetMain, SrpUserRequest

SrpFleetMainList = GenericList(SrpFleetMain, model_serializer=SrpFleetMainSerializer)
SrpFleetMainDetail = GenericModel(SrpFleetMain, model_serializer=SrpFleetMainSerializer)
SrpUserRequestList = GenericList(SrpUserRequest, model_serializer=SrpUserRequestSerializer)
SrpUserRequestDetail = GenericModel(SrpUserRequest, model_serializer=SrpUserRequestSerializer)
