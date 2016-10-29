from __future__ import unicode_literals

from rest_framework import routers
from authapi.optimer.views import optimerViewSet

router = routers.SimpleRouter()
router.register('optimer', optimerViewSet)

urlpatterns = router.urls

