from django.contrib import admin
from .models import AuthTS
from .models import DiscordAuthToken
from .models import MumbleUser
from .models import GroupCache

class AuthTSgroupAdmin(admin.ModelAdmin):
    fields = ['auth_group','ts_group']
    filter_horizontal = ('ts_group',)

admin.site.register(AuthTS, AuthTSgroupAdmin)

admin.site.register(DiscordAuthToken)

admin.site.register(MumbleUser)

admin.site.register(GroupCache)
