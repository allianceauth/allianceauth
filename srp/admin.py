from __future__ import unicode_literals
from django.contrib import admin

from srp.models import SrpFleetMain
from srp.models import SrpUserRequest

admin.site.register(SrpFleetMain)
admin.site.register(SrpUserRequest)
