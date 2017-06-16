from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase
from django.contrib.auth.models import User
from alliance_auth.tests.auth_utils import AuthUtils
from authentication.models import CharacterOwnership, UserProfile, State, get_guest_state
from authentication.backends import StateBackend
from eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from esi.models import Token


class BackendTestCase(TestCase):
    def setUp(self):
        self.main_character = EveCharacter.objects.create(
            character_id=1,
            character_name='Main Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )
        self.alt_character = EveCharacter.objects.create(
            character_id=2,
            character_name='Alt Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )
        self.unclaimed_character = EveCharacter.objects.create(
            character_id=3,
            character_name='Unclaimed Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )
        self.user = AuthUtils.create_user('test_user', disconnect_signals=True)
        AuthUtils.disconnect_signals()
        CharacterOwnership.objects.create(user=self.user, character=self.main_character, owner_hash='1')
        CharacterOwnership.objects.create(user=self.user, character=self.alt_character, owner_hash='2')
        UserProfile.objects.update_or_create(user=self.user, defaults={'main_character': self.main_character})
        AuthUtils.connect_signals()

    def test_authenticate_main_character(self):
        t = Token(character_id=self.main_character.character_id, character_owner_hash='1')
        user = StateBackend().authenticate(token=t)
        self.assertEquals(user, self.user)

    def test_authenticate_alt_character(self):
        t = Token(character_id=self.alt_character.character_id, character_owner_hash='2')
        user = StateBackend().authenticate(token=t)
        self.assertEquals(user, self.user)

    def test_authenticate_unclaimed_character(self):
        t = Token(character_id=self.unclaimed_character.character_id, character_name=self.unclaimed_character.character_name, character_owner_hash='3')
        user = StateBackend().authenticate(token=t)
        self.assertNotEqual(user, self.user)
        self.assertEqual(user.username, 'Unclaimed_Character')
        self.assertEqual(user.profile.main_character, self.unclaimed_character)

    def test_iterate_username(self):
        t = Token(character_id=self.unclaimed_character.character_id,
                  character_name=self.unclaimed_character.character_name, character_owner_hash='3')
        username = StateBackend().authenticate(token=t).username
        t.character_owner_hash = '4'
        username_1 = StateBackend().authenticate(token=t).username
        t.character_owner_hash = '5'
        username_2 = StateBackend().authenticate(token=t).username
        self.assertNotEqual(username, username_1, username_2)
        self.assertTrue(username_1.endswith('_1'))
        self.assertTrue(username_2.endswith('_2'))


class CharacterOwnershipTestCase(TestCase):
    def setUp(self):
        self.user = AuthUtils.create_user('user', disconnect_signals=True)
        self.alt_user = AuthUtils.create_user('alt_user', disconnect_signals=True)
        self.character = EveCharacter.objects.create(
            character_id=1,
            character_name='Main Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )

    def test_create_ownership(self):
        Token.objects.create(
            user=self.user,
            character_id=self.character.character_id,
            character_name=self.character.character_name,
            character_owner_hash='1',
        )
        co = CharacterOwnership.objects.get(character=self.character)
        self.assertEquals(co.user, self.user)
        self.assertEquals(co.owner_hash, '1')

    def test_transfer_ownership(self):
        Token.objects.create(
            user=self.user,
            character_id=self.character.character_id,
            character_name=self.character.character_name,
            character_owner_hash='1',
        )
        Token.objects.create(
            user=self.alt_user,
            character_id=self.character.character_id,
            character_name=self.character.character_name,
            character_owner_hash='2',
        )
        co = CharacterOwnership.objects.get(character=self.character)
        self.assertNotEqual(self.user, co.user)
        self.assertEquals(self.alt_user, co.user)

    def test_clear_main_character(self):
        Token.objects.create(
            user=self.user,
            character_id=self.character.character_id,
            character_name=self.character.character_name,
            character_owner_hash='1',
        )
        self.user.profile.main_character = self.character
        self.user.profile.save()
        Token.objects.create(
            user=self.alt_user,
            character_id=self.character.character_id,
            character_name=self.character.character_name,
            character_owner_hash='2',
        )
        self.user = User.objects.get(pk=self.user.pk)
        self.assertIsNone(self.user.profile.main_character)


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

    def _refresh_user(self):
        self.user = User.objects.get(pk=self.user.pk)

    def test_state_assignment_on_character_change(self):
        self.member_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.member_state)

        self.member_state.member_characters.remove(self.test_character)
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.guest_state)

    def test_state_assignment_on_corporation_change(self):
        self.member_state.member_corporations.add(self.test_corporation)
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.member_state)

        self.member_state.member_corporations.remove(self.test_corporation)
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.guest_state)

    def test_state_assignment_on_alliance_addition(self):
        self.member_state.member_alliances.add(self.test_alliance)
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.member_state)

        self.member_state.member_alliances.remove(self.test_alliance)
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.guest_state)

    def test_state_assignment_on_higher_priority_state_creation(self):
        self.member_state.member_characters.add(self.test_character)
        self.higher_state = State.objects.create(
            name='Higher State',
            priority=200,
        )
        self.higher_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.assertEquals(self.higher_state, self.user.profile.state)
        self.higher_state.member_characters.clear()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
        self.member_state.member_characters.clear()

    def test_state_assignment_on_lower_priority_state_creation(self):
        self.member_state.member_characters.add(self.test_character)
        self.lower_state = State.objects.create(
            name='Lower State',
            priority=125,
        )
        self.lower_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
        self.lower_state.member_characters.clear()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
        self.member_state.member_characters.clear()

    def test_state_assignment_on_priority_change(self):
        self.member_state.member_characters.add(self.test_character)
        self.lower_state = State.objects.create(
            name='Lower State',
            priority=125,
        )
        self.lower_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.lower_state.priority = 500
        self.lower_state.save()
        self._refresh_user()
        self.assertEquals(self.lower_state, self.user.profile.state)
        self.lower_state.priority = 125
        self.lower_state.save()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)

    def test_state_assignment_on_state_deletion(self):
        self.member_state.member_characters.add(self.test_character)
        self.higher_state = State.objects.create(
            name='Higher State',
            priority=200,
        )
        self.higher_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.assertEquals(self.higher_state, self.user.profile.state)
        self.higher_state.delete()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
