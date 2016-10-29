from authapi.timerboard.serializers import TimerSerializer, TimerExpandedSerializer
from authapi.views import GenericModelViewSet
from timerboard.models import Timer

TimerViewSet = GenericModelViewSet(Timer,serializers = {'default':TimerSerializer, 'retrieve':TimerExpandedSerializer})
