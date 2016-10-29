from __future__ import unicode_literals

from rest_framework import routers
import authapi.srp.views

router = routers.SimpleRouter()
router.register('srpfleetmain', authapi.srp.views.SrpFleetMainViewSet)
router.register('srpuserrequest', authapi.srp.views.SrpUserRequestViewSet)

urlpatterns = router.urls
