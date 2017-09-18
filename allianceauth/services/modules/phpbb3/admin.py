from django.contrib import admin
from .models import Phpbb3User


class Phpbb3UserAdmin(admin.ModelAdmin):
        list_display = ('user', 'username')
        search_fields = ('user__username', 'username')

admin.site.register(Phpbb3User, Phpbb3UserAdmin)
