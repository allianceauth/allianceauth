from django.contrib import admin
from .models import OpenfireUser


class OpenfireUserAdmin(admin.ModelAdmin):
        list_display = ('user', 'username')
        search_fields = ('user__username', 'username')

admin.site.register(OpenfireUser, OpenfireUserAdmin)
