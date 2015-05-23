from django.contrib import admin
from .models import authTS
from .models import TSgroup
from .models import userTSgroup

class AuthTSgroupAdmin(admin.ModelAdmin):
	fields = ['ts_group_id','auth_group_id']

class TSgroupAdmin(admin.ModelAdmin):
	fields = ['name']

admin.site.register(authTS, AuthTSgroupAdmin)
admin.site.register(TSgroup, TSgroupAdmin)