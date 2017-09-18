from django.contrib import admin
from .models import MumbleUser


class MumbleUserAdmin(admin.ModelAdmin):
        fields = ('user', 'username', 'groups')  # pwhash is hidden from admin panel
        list_display = ('user', 'username', 'groups')
        search_fields = ('user__username', 'username', 'groups')

admin.site.register(MumbleUser, MumbleUserAdmin)
