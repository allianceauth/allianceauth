from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.text import slugify
from django import forms
from django.db.models.signals import post_save
from authentication.models import State, get_guest_state, CharacterOwnership, UserProfile
from authentication.signals import reassess_on_profile_save
from alliance_auth.hooks import get_hooks
from services.hooks import ServicesHook
from services.tasks import validate_services


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


class StateForm(forms.ModelForm):
    def _is_none_state(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance == get_guest_state()

    def __init__(self, *args, **kwargs):
        super(StateForm, self).__init__(*args, **kwargs)
        if self._is_none_state():
            self.fields['name'].widget.attrs['readonly'] = True

    def clean_name(self):
        if self._is_none_state():
            return self.instance.name
        return self.cleaned_data['name']


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    form = StateForm

    fieldsets = (
        (None, {
            'fields': ('name', 'permissions', 'priority'),
        }),
        ('Membership', {
            'classes': ('collapse',),
            'fields': ('public', 'member_characters', 'member_corporations', 'member_alliances'),
        })
    )

    filter_horizontal = ['member_characters', 'member_corporations', 'member_alliances', 'permissions']

    @staticmethod
    def has_delete_permission(request, obj=None):
        if obj == get_guest_state():
            return False


admin.site.register(CharacterOwnership)


class UserProfileAdminForm(forms.ModelForm):
    def save(self, *args, **kwargs):
        # prevent state reassessment to allow manually overriding states
        post_save.disconnect(reassess_on_profile_save, sender=UserProfile)
        model = super(UserProfileAdminForm, self).save(*args, **kwargs)
        post_save.connect(reassess_on_profile_save, sender=UserProfile)
        validate_services(model.user)
        return model


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm
