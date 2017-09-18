from django.contrib import admin
from .models import DiscordUser


class DiscordUserAdmin(admin.ModelAdmin):
        list_display = ('user', 'uid')
        search_fields = ('user__username', 'uid')

admin.site.register(DiscordUser, DiscordUserAdmin)
