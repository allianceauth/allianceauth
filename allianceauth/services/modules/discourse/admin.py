from django.contrib import admin
from .models import DiscourseUser


class DiscourseUserAdmin(admin.ModelAdmin):
        list_display = ('user',)
        search_fields = ('user__username',)

admin.site.register(DiscourseUser, DiscourseUserAdmin)
