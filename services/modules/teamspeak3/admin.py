from __future__ import unicode_literals
from django.contrib import admin
from .models import AuthTS, Teamspeak3User


class Teamspeak3UserAdmin(admin.ModelAdmin):
        list_display = ('user', 'uid', 'perm_key')
        search_fields = ('user__username', 'uid', 'perm_key')


class AuthTSgroupAdmin(admin.ModelAdmin):
    fields = ['auth_group', 'ts_group']
    filter_horizontal = ('ts_group',)


admin.site.register(AuthTS, AuthTSgroupAdmin)
admin.site.register(Teamspeak3User, Teamspeak3UserAdmin)
