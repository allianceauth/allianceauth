import authapi.auth.views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('user', authapi.auth.views.UserViewSet)
router.register('permission', authapi.auth.views.PermissionViewSet)
router.register('group', authapi.auth.views.GroupViewSet)

urlpatterns = router.urls
