from __future__ import unicode_literals
from django.contrib import admin

from groupmanagement.models import GroupRequest
from groupmanagement.models import AuthGroup


class AuthGroupAdmin(admin.ModelAdmin):
    """
    Admin model for AuthGroup
    """
    filter_horizontal = ('group_leaders',)

admin.site.register(GroupRequest)
admin.site.register(AuthGroup, AuthGroupAdmin)
