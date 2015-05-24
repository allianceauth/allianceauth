from django.contrib import admin
from .models import AuthTS
from .models import TSgroup
from .models import UserTSgroup

class AuthTSgroupAdmin(admin.ModelAdmin):
	fields = ['ts_group_id','auth_group_id']

class TSgroupAdmin(admin.ModelAdmin):
	fields = ['name']

admin.site.register(AuthTS, AuthTSgroupAdmin)
admin.site.register(TSgroup, TSgroupAdmin)