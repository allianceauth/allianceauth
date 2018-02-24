from django.contrib import admin
from django.contrib.auth.models import Group as BaseGroup
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, m2m_changed
from django.dispatch import receiver
from .models import AuthGroup
from .models import GroupRequest


class AuthGroupInlineAdmin(admin.StackedInline):
    model = AuthGroup
    filter_horizontal = ('group_leaders',)
    fields = ('description', 'group_leaders', 'internal', 'hidden', 'open', 'public')
    verbose_name_plural = 'Auth Settings'
    verbose_name = ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('auth.change_group')


class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)
    inlines = (AuthGroupInlineAdmin,)


class Group(BaseGroup):
    class Meta:
        proxy = True
        verbose_name = BaseGroup._meta.verbose_name
        verbose_name_plural = BaseGroup._meta.verbose_name_plural

try:
    admin.site.unregister(BaseGroup)
finally:
    admin.site.register(Group, GroupAdmin)


admin.site.register(GroupRequest)


@receiver(pre_save, sender=Group)
def redirect_pre_save(sender, signal=None, *args, **kwargs):
    pre_save.send(BaseGroup, *args, **kwargs)


@receiver(post_save, sender=Group)
def redirect_post_save(sender, signal=None, *args, **kwargs):
    post_save.send(BaseGroup, *args, **kwargs)


@receiver(pre_delete, sender=Group)
def redirect_pre_delete(sender, signal=None, *args, **kwargs):
    pre_delete.send(BaseGroup, *args, **kwargs)


@receiver(post_delete, sender=Group)
def redirect_post_delete(sender, signal=None, *args, **kwargs):
    post_delete.send(BaseGroup, *args, **kwargs)


@receiver(m2m_changed, sender=Group.permissions.through)
def redirect_m2m_changed_permissions(sender, signal=None, *args, **kwargs):
    m2m_changed.send(BaseGroup, *args, **kwargs)