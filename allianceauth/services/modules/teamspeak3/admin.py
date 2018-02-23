from django.contrib import admin
from .models import AuthTS, Teamspeak3User, StateGroup


class Teamspeak3UserAdmin(admin.ModelAdmin):
        list_display = ('user', 'uid', 'perm_key')
        search_fields = ('user__username', 'uid', 'perm_key')


class AuthTSgroupAdmin(admin.ModelAdmin):
    fields = ['auth_group', 'ts_group']
    filter_horizontal = ('ts_group',)


@admin.register(StateGroup)
class StateGroupAdmin(admin.ModelAdmin):
    list_display = ('state', 'ts_group')
    search_fields = ('state__name', 'ts_group__ts_group_name')


admin.site.register(AuthTS, AuthTSgroupAdmin)
admin.site.register(Teamspeak3User, Teamspeak3UserAdmin)
