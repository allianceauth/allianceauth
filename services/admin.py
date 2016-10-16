from __future__ import unicode_literals
from django.contrib import admin
from services.models import AuthTS
from services.models import MumbleUser
from services.models import GroupCache


class AuthTSgroupAdmin(admin.ModelAdmin):
    fields = ['auth_group', 'ts_group']
    filter_horizontal = ('ts_group',)


admin.site.register(AuthTS, AuthTSgroupAdmin)

admin.site.register(MumbleUser)

admin.site.register(GroupCache)
