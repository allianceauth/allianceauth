from __future__ import unicode_literals
from django.contrib import admin
from .models import IpboardUser


class IpboardUserAdmin(admin.ModelAdmin):
        list_display = ('user', 'username')
        search_fields = ('user__username', 'username')

admin.site.register(IpboardUser, IpboardUserAdmin)
