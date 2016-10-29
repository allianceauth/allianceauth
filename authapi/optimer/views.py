from authapi.optimer.serializers import optimerSerializer, optimerExpandedSerializer
from authapi.views import GenericModelViewSet
from optimer.models import optimer

optimerViewSet = GenericModelViewSet(optimer, serializers={'default':optimerSerializer, 'retrieve':optimerExpandedSerializer})
