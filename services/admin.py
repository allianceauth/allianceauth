from django.contrib import admin
from .models import AuthTS
from .models import TSgroup
from .models import UserTSgroup
from .models import DiscordAuthToken

class AuthTSgroupAdmin(admin.ModelAdmin):
	fields = ['auth_group','ts_group']
	filter_horizontal = ('ts_group',)

class TSgroupAdmin(admin.ModelAdmin):
	fields = ['ts_group_name']

class UserTSgroupAdmin(admin.ModelAdmin):
	fields = ['user','ts_group']
	filter_horizontal = ('ts_group',)

admin.site.register(AuthTS, AuthTSgroupAdmin)
admin.site.register(TSgroup, TSgroupAdmin)

admin.site.register(DiscordAuthToken)
