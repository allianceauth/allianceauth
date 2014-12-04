from django.contrib import admin

from models import SrpFleetMain
from models import SrpUserRequest

# Register your models here.
admin.site.register(SrpFleetMain)
admin.site.register(SrpUserRequest)