from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from authentication.models import UserProfile


class StateBackend(ModelBackend):
    @staticmethod
    def _get_state_permissions(user_obj):
        profile_state_field = UserProfile._meta.get_field('state')
        user_state_query = 'state__%s__user' % profile_state_field.related_query_name()
        return Permission.objects.filter(**{user_state_query: user_obj})

    def get_state_permission(self, user_obj, obj=None):
        return self._get_permissions(user_obj, obj, 'state')

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = self.get_user_permissions(user_obj)
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
            user_obj._perm_cache.update(self.get_state_permissions(user_obj))
        return user_obj._perm_cache
