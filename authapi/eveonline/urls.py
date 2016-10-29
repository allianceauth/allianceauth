from __future__ import unicode_literals

import authapi.eveonline.views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('evecharacter', authapi.eveonline.views.EveCharacterViewSet)
router.register('evecorporationinfo', authapi.eveonline.views.EveCorporationInfoViewSet)
router.register('eveallianceinfo', authapi.eveonline.views.EveAllianceInfoViewSet)
router.register('eveapikeypair', authapi.eveonline.views.EveApiKeyPairViewSet)
urlpatterns = router.urls
