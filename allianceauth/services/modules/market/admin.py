from django.contrib import admin
from .models import MarketUser


class MarketUserAdmin(admin.ModelAdmin):
        list_display = ('user', 'username')
        search_fields = ('user__username', 'username')

admin.site.register(MarketUser, MarketUserAdmin)
