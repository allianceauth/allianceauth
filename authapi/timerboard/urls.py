from __future__ import unicode_literals

from rest_framework import routers
import authapi.timerboard.views

router = routers.SimpleRouter()
router.register(r'timer', authapi.timerboard.views.TimerViewSet)

urlpatterns = router.urls
