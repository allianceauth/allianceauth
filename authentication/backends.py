from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from authentication.models import UserProfile, CharacterOwnership
from django.contrib.auth.models import User


class StateBackend(ModelBackend):
    @staticmethod
    def _get_state_permissions(user_obj):
        profile_state_field = UserProfile._meta.get_field('state')
        user_state_query = 'state__%s__user' % profile_state_field.related_query_name()
        return Permission.objects.filter(**{user_state_query: user_obj})

    def get_state_permissions(self, user_obj, obj=None):
        return self._get_permissions(user_obj, obj, 'state')

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = self.get_user_permissions(user_obj)
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
            user_obj._perm_cache.update(self.get_state_permissions(user_obj))
        return user_obj._perm_cache

    def authenticate(self, token=None):
        if not token:
            return None
        try:
            ownership = CharacterOwnership.objects.get(character__character_id=token.character_id)
            if ownership.owner_hash == token.character_owner_hash:
                return ownership.user
            else:
                ownership.delete()
                return self.create_user(token)
        except CharacterOwnership.DoesNotExist:
            try:
                # insecure legacy main check for pre-sso registration auth installs
                profile = UserProfile.objects.get(main_character__character_id=token.character_id)
                # attach an ownership
                CharacterOwnership.objects.create_by_token(token)
                return profile.user
            except UserProfile.DoesNotExist:
                pass
            return self.create_user(token)

    def create_user(self, token):
        username = self.iterate_username(token.charater_name)  # build unique username off character name
        user = User.objects.create_user(username)
        user.set_unusable_password()  # prevent login via password
        user.is_active = False  # prevent login until email set
        user.save()
        token.user = user
        co = CharacterOwnership.objects.create_by_token(token)  # assign ownership to this user
        user.profile.main_character = co.character  # assign main character as token character
        user.profile.save()
        return user

    @staticmethod
    def iterate_username(name):
        if User.objects.filter(username__startswith=name).exists():
            u = User.objects.filter(username__startswith=name)
            num = len(u)
            username = "%s_%s" % (name, num)
            while u.filter(username=username).exists():
                num += 1
                username = "%s_%s" % (name, num)
        else:
            username = name
        return username
