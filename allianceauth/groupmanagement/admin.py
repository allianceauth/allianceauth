from django.contrib import admin
from django.contrib.auth.models import Group

from .models import AuthGroup
from .models import GroupRequest


class AuthGroupAdmin(admin.ModelAdmin):
    """
    Admin model for AuthGroup
    """
    filter_horizontal = ('group_leaders',)


class ProxyGroup(Group):
    class Meta:
        proxy = True
        verbose_name = Group._meta.verbose_name
        verbose_name_plural = Group._meta.verbose_name_plural

try:
    admin.site.unregister(Group)
finally:
    admin.site.register(ProxyGroup)


admin.site.register(GroupRequest)
admin.site.register(AuthGroup, AuthGroupAdmin)
