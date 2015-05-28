from django.contrib import admin
from .models import AuthTS
from .models import TSgroup
from .models import UserTSgroup

class AuthTSgroupAdmin(admin.ModelAdmin):
	fields = ['auth_group','ts_group']
	filter_horizontal = ('ts_group',)

class TSgroupAdmin(admin.ModelAdmin):
	fields = ['ts_group_name']

admin.site.register(AuthTS, AuthTSgroupAdmin)
admin.site.register(TSgroup, TSgroupAdmin)