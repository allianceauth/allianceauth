from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase
from alliance_auth.tests.auth_utils import AuthUtils
from authentication.models import State, get_guest_state
from eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo


class StateTestCase(TestCase):
    def setUp(self):
        self.user = AuthUtils.create_user('test_user', disconnect_signals=True)
        AuthUtils.add_main_character(self.user, 'Test Character', '1', corp_id='1', alliance_id='1',
                                     corp_name='Test Corp', alliance_name='Test Alliance')
        self.guest_state = get_guest_state()
        self.test_character = EveCharacter.objects.get(character_id='1')
        self.test_corporation = EveCorporationInfo.objects.create(corporation_id='1', corporation_name='Test Corp',
                                                                  corporation_ticker='TEST', member_count=1)
        self.test_alliance = EveAllianceInfo.objects.create(alliance_id='1', alliance_name='Test Alliance',
                                                            alliance_ticker='TEST', executor_corp_id='1')
        self.member_state = State.objects.create(
            name='Test Member',
            priority=150,
        )

    def test_state_assignment_on_character_change(self):
        self.member_state.member_characters.add(self.test_character)
        self.assertEquals(self.user.profile.state, self.member_state)

        self.member_state.member_characters.remove(self.test_character)
        self.assertEquals(self.user.profile.state, self.guest_state)

    def test_state_assignment_on_corporation_change(self):
        self.member_state.member_corporations.add(self.test_corporation)
        self.assertEquals(self.user.profile.state, self.member_state)

        self.member_state.member_corporations.remove(self.test_corporation)
        self.assertEquals(self.user.profile.state, self.guest_state)

    def test_state_assignment_on_alliance_addition(self):
        self.member_state.member_alliances.add(self.test_alliance)
        self.assertEquals(self.user.profile.state, self.member_state)

        self.member_state.member_alliances.remove(self.test_alliance)
        self.assertEquals(self.user.profile.state, self.guest_state)
