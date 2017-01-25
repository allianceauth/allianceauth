from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.text import slugify

from authentication.models import AuthServicesInfo
from eveonline.models import EveCharacter
from alliance_auth.hooks import get_hooks
from services.hooks import ServicesHook


@admin.register(AuthServicesInfo)
class AuthServicesInfoManager(admin.ModelAdmin):

    @staticmethod
    def main_character(obj):
        if obj.main_char_id:
            try:
                return EveCharacter.objects.get(character_id=obj.main_char_id)
            except EveCharacter.DoesNotExist:
                pass
        return None

    @staticmethod
    def has_delete_permission(request, obj=None):
        return False

    @staticmethod
    def has_add_permission(request, obj=None):
        return False

    search_fields = [
        'user__username',
        'main_char_id',
    ]
    list_display = ('user', 'main_character')


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

# Re-register UserAdmin
try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, UserAdmin)
