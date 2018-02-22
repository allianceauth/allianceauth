from django.contrib import admin
from django.contrib.auth.models import Group as BaseGroup
from django.db.models.signals import post_save

from .models import AuthGroup, save_auth_group, create_auth_group
from .models import GroupRequest


class AuthGroupAdmin(admin.ModelAdmin):
    """
    Admin model for AuthGroup
    """
    filter_horizontal = ('group_leaders',)


class Group(BaseGroup):
    class Meta:
        proxy = True
        verbose_name = BaseGroup._meta.verbose_name
        verbose_name_plural = BaseGroup._meta.verbose_name_plural

try:
    admin.site.unregister(BaseGroup)
finally:
    admin.site.register(Group)


admin.site.register(GroupRequest)
admin.site.register(AuthGroup, AuthGroupAdmin)


post_save.connect(create_auth_group, sender=Group)
post_save.connect(save_auth_group, sender=Group)
