from django.contrib import admin
from .models import SeatUser


class SeatUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'username')
    search_fields = ('user__username', 'username')

admin.site.register(SeatUser, SeatUserAdmin)
