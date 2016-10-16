from __future__ import unicode_literals
from django.contrib.auth.decorators import user_passes_test
from authentication.models import AuthServicesInfo
from authentication.states import MEMBER_STATE, BLUE_STATE, NONE_STATE
from django.conf import settings


def _state_required(states, *args, **kwargs):
    def test_func(user):
        if user.is_superuser and settings.SUPERUSER_STATE_BYPASS:
            return True
        if user.is_authenticated:
            auth = AuthServicesInfo.objects.get_or_create(user=user)[0]
            return auth.state in states
        return False

    return user_passes_test(test_func, *args, **kwargs)


def members(*args, **kwargs):
    return _state_required([MEMBER_STATE], *args, **kwargs)


def blues(*args, **kwargs):
    return _state_required([BLUE_STATE], *args, **kwargs)


def members_and_blues(*args, **kwargs):
    return _state_required([MEMBER_STATE, BLUE_STATE], *args, **kwargs)


def none_state(*args, **kwargs):
    return _state_required([NONE_STATE], *args, **kwargs)
