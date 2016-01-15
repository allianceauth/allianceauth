from django.contrib import admin
from .models import AuthTS
from .models import DiscordAuthToken

class AuthTSgroupAdmin(admin.ModelAdmin):
    fields = ['auth_group','ts_group']
    filter_horizontal = ('ts_group',)

admin.site.register(AuthTS, AuthTSgroupAdmin)

admin.site.register(DiscordAuthToken)
