from django.contrib import admin

from models import GroupDescription
from models import GroupRequest
from models import HiddenGroup
from models import OpenGroup


admin.site.register(GroupDescription)
admin.site.register(GroupRequest)
admin.site.register(HiddenGroup)
admin.site.register(OpenGroup)
