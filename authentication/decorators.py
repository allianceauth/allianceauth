from __future__ import unicode_literals
from django.contrib.auth.decorators import user_passes_test
from authentication.managers import UserState


def _state_required(state_test, *args, **kwargs):
    return user_passes_test(state_test, *args, **kwargs)


def members(*args, **kwargs):
    return _state_required(UserState.member_state, *args, **kwargs)


def blues(*args, **kwargs):
    return _state_required(UserState.blue_state, *args, **kwargs)


def members_and_blues(*args, **kwargs):
    return _state_required(UserState.member_or_blue_state, *args, **kwargs)


def none_state(*args, **kwargs):
    return _state_required(UserState.none_state, *args, **kwargs)
