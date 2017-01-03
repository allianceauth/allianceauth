from __future__ import unicode_literals
from authentication.states import NONE_STATE, BLUE_STATE, MEMBER_STATE
from authentication.managers import UserState
from django.conf import settings


def membership_state(request):
    return UserState.get_membership_state(request)


def states(request):
    return {
        'BLUE_STATE': BLUE_STATE,
        'MEMBER_STATE': MEMBER_STATE,
        'NONE_STATE': NONE_STATE,
        'MEMBER_BLUE_STATE': [MEMBER_STATE, BLUE_STATE],
    }
