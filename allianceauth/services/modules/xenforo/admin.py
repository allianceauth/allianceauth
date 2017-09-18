from django.contrib import admin
from .models import XenforoUser


class XenforoUserAdmin(admin.ModelAdmin):
        list_display = ('user', 'username')
        search_fields = ('user__username', 'username')

admin.site.register(XenforoUser, XenforoUserAdmin)
