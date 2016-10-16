from __future__ import unicode_literals
from django.contrib import admin

from groupmanagement.models import GroupDescription
from groupmanagement.models import GroupRequest
from groupmanagement.models import HiddenGroup
from groupmanagement.models import OpenGroup


admin.site.register(GroupDescription)
admin.site.register(GroupRequest)
admin.site.register(HiddenGroup)
admin.site.register(OpenGroup)
