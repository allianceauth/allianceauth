from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Permission
from django.utils.text import slugify
from allianceauth.services.hooks import ServicesHook

from allianceauth.authentication.models import State, get_guest_state, CharacterOwnership, UserProfile
from allianceauth.hooks import get_hooks


def make_service_hooks_update_groups_action(service):
    """
    Make a admin action for the given service
    :param service: services.hooks.ServicesHook
    :return: fn to update services groups for the selected users
    """
    def update_service_groups(modeladmin, request, queryset):
        for user in queryset:  # queryset filtering doesn't work here?
            service.update_groups(user)

    update_service_groups.__name__ = str('update_{}_groups'.format(slugify(service.name)))
    update_service_groups.short_description = "Sync groups for selected {} accounts".format(service.title)
    return update_service_groups


def make_service_hooks_sync_nickname_action(service):
    """
    Make a sync_nickname admin action for the given service
    :param service: services.hooks.ServicesHook
    :return: fn to sync nickname for the selected users
    """
    def sync_nickname(modeladmin, request, queryset):
        for user in queryset:  # queryset filtering doesn't work here?
            service.sync_nickname(user)

    sync_nickname.__name__ = str('sync_{}_nickname'.format(slugify(service.name)))
    sync_nickname.short_description = "Sync nicknames for selected {} accounts".format(service.title)
    return sync_nickname


class UserAdmin(BaseUserAdmin):
    """
    Extending Django's UserAdmin model
    """
    def get_actions(self, request):
        actions = super(BaseUserAdmin, self).get_actions(request)

        for hook in get_hooks('services_hook'):
            svc = hook()
            # Check update_groups is redefined/overloaded
            if svc.update_groups.__module__ != ServicesHook.update_groups.__module__:
                action = make_service_hooks_update_groups_action(svc)
                actions[action.__name__] = (action,
                                            action.__name__,
                                            action.short_description)
            # Create sync nickname action if service implements it
            if svc.sync_nickname.__module__ != ServicesHook.sync_nickname.__module__:
                action = make_service_hooks_sync_nickname_action(svc)
                actions[action.__name__] = (action,
                                            action.__name__,
                                            action.short_description)

        return actions
    list_filter = BaseUserAdmin.list_filter + ('profile__state',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'permissions', 'priority'),
        }),
        ('Membership', {
            'fields': ('public', 'member_characters', 'member_corporations', 'member_alliances'),
        })
    )
    filter_horizontal = ['member_characters', 'member_corporations', 'member_alliances', 'permissions']
    list_display = ('name', 'priority', 'user_count')

    def has_delete_permission(self, request, obj=None):
        if obj == get_guest_state():
            return False
        return super(StateAdmin, self).has_delete_permission(request, obj=obj)

    def get_fieldsets(self, request, obj=None):
        if obj == get_guest_state():
            return (
                (None, {
                    'fields': ('permissions', 'priority'),
                }),
            )
        return super(StateAdmin, self).get_fieldsets(request, obj=obj)

    @staticmethod
    def user_count(obj):
        return obj.userprofile_set.all().count()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'state')
    search_fields = ('user__username', 'main_character__character_name')
    list_filter = ('state',)
    list_display = ('user', 'main_character')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CharacterOwnership)
class CharacterOwnershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'character')
    search_fields = ('user__username', 'character__character_name', 'character__corporation_name', 'character__alliance_name')
    readonly_fields = ('owner_hash', 'character')


class PermissionAdmin(admin.ModelAdmin):
    actions = None
    readonly_fields = [field.name for field in Permission._meta.fields]
    list_display = ('admin_name', 'name', 'codename', 'content_type')
    list_filter = ('content_type__app_label',)

    @staticmethod
    def admin_name(obj):
        return str(obj)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Hack to allow registration of django.contrib.auth models in our authentication app
class ProxyUser(User):
    class Meta:
        proxy = True
        verbose_name = User._meta.verbose_name
        verbose_name_plural = User._meta.verbose_name_plural


class ProxyPermission(Permission):
    class Meta:
        proxy = True
        verbose_name = Permission._meta.verbose_name
        verbose_name_plural = Permission._meta.verbose_name_plural

try:
    admin.site.unregister(User)
finally:
    admin.site.register(ProxyUser, UserAdmin)
    admin.site.register(ProxyPermission, PermissionAdmin)