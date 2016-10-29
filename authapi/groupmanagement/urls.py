from rest_framework import routers
from authapi.groupmanagement.views import GroupRequestViewSet

router = routers.SimpleRouter()
router.register('grouprequest', GroupRequestViewSet)

urlpatterns = router.urls
