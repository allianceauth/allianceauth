from django.contrib import admin

from allianceauth.srp.models import SrpFleetMain
from allianceauth.srp.models import SrpUserRequest

admin.site.register(SrpFleetMain)
admin.site.register(SrpUserRequest)
