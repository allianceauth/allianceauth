from unittest import mock
from io import StringIO
from django.test import TestCase
from django.contrib.auth.models import User
from allianceauth.tests.auth_utils import AuthUtils
from .models import CharacterOwnership, UserProfile, State, get_guest_state, OwnershipRecord
from .backends import StateBackend
from .tasks import check_character_ownership
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from esi.models import Token
from esi.errors import IncompleteResponseError
from allianceauth.authentication.decorators import main_character_required
from django.test.client import RequestFactory
from django.http.response import HttpResponse
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.shortcuts import reverse
from django.core.management import call_command
from urllib import parse

MODULE_PATH = 'allianceauth.authentication'


class DecoratorTestCase(TestCase):
    @staticmethod
    @main_character_required
    def dummy_view(*args, **kwargs):
        return HttpResponse(status=200)

    @classmethod
    def setUpTestData(cls):
        cls.main_user = AuthUtils.create_user('main_user', disconnect_signals=True)
        cls.no_main_user = AuthUtils.create_user('no_main_user', disconnect_signals=True)
        main_character = EveCharacter.objects.create(
            character_id=1,
            character_name='Main Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )
        CharacterOwnership.objects.create(user=cls.main_user, character=main_character, owner_hash='1')
        cls.main_user.profile.main_character = main_character

    def setUp(self):
        self.request = RequestFactory().get('/test/')

    @mock.patch(MODULE_PATH + '.decorators.messages')
    def test_login_redirect(self, m):
        setattr(self.request, 'user', AnonymousUser())
        response = self.dummy_view(self.request)
        self.assertEqual(response.status_code, 302)
        url = getattr(response, 'url', None)
        self.assertEqual(parse.urlparse(url).path,  reverse(settings.LOGIN_URL))

    @mock.patch(MODULE_PATH + '.decorators.messages')
    def test_main_character_redirect(self, m):
        setattr(self.request, 'user', self.no_main_user)
        response = self.dummy_view(self.request)
        self.assertEqual(response.status_code, 302)
        url = getattr(response, 'url', None)
        self.assertEqual(url, reverse('authentication:dashboard'))

    @mock.patch(MODULE_PATH + '.decorators.messages')
    def test_successful_request(self, m):
        setattr(self.request, 'user', self.main_user)
        response = self.dummy_view(self.request)
        self.assertEqual(response.status_code, 200)


class BackendTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.main_character = EveCharacter.objects.create(
            character_id=1,
            character_name='Main Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )
        cls.alt_character = EveCharacter.objects.create(
            character_id=2,
            character_name='Alt Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )
        cls.unclaimed_character = EveCharacter.objects.create(
            character_id=3,
            character_name='Unclaimed Character',
            corporation_id=1,
            corporation_name='Corp',
            corporation_ticker='CORP',
        )
        cls.user = AuthUtils.create_user('test_user', disconnect_signals=True)
        cls.old_user = AuthUtils.create_user('old_user', disconnect_signals=True)
        AuthUtils.disconnect_signals()
        CharacterOwnership.objects.create(user=cls.user, character=cls.main_character, owner_hash='1')
        CharacterOwnership.objects.create(user=cls.user, character=cls.alt_character, owner_hash='2')
        UserProfile.objects.update_or_create(user=cls.user, defaults={'main_character': cls.main_character})
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

    def test_authenticate_character_record(self):
        t = Token(character_id=self.unclaimed_character.character_id, character_name=self.unclaimed_character.character_name, character_owner_hash='4')
        record = OwnershipRecord.objects.create(user=self.old_user, character=self.unclaimed_character, owner_hash='4')
        user = StateBackend().authenticate(t)
        self.assertEqual(user, self.old_user)
        self.assertTrue(CharacterOwnership.objects.filter(owner_hash='4', user=self.old_user).exists())
        self.assertTrue(user.profile.main_character)

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
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('user', disconnect_signals=True)
        cls.alt_user = AuthUtils.create_user('alt_user', disconnect_signals=True)
        cls.character = EveCharacter.objects.create(
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
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('test_user', disconnect_signals=True)
        AuthUtils.add_main_character(cls.user, 'Test Character', '1', corp_id='1', alliance_id='1',
                                     corp_name='Test Corp', alliance_name='Test Alliance')
        cls.guest_state = get_guest_state()
        cls.test_character = EveCharacter.objects.get(character_id='1')
        cls.test_corporation = EveCorporationInfo.objects.create(corporation_id='1', corporation_name='Test Corp',
                                                                  corporation_ticker='TEST', member_count=1)
        cls.test_alliance = EveAllianceInfo.objects.create(alliance_id='1', alliance_name='Test Alliance',
                                                            alliance_ticker='TEST', executor_corp_id='1')
        cls.member_state = State.objects.create(
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
        higher_state = State.objects.create(
            name='Higher State',
            priority=200,
        )
        higher_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.assertEquals(higher_state, self.user.profile.state)
        higher_state.member_characters.clear()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
        self.member_state.member_characters.clear()

    def test_state_assignment_on_lower_priority_state_creation(self):
        self.member_state.member_characters.add(self.test_character)
        lower_state = State.objects.create(
            name='Lower State',
            priority=125,
        )
        lower_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
        lower_state.member_characters.clear()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
        self.member_state.member_characters.clear()

    def test_state_assignment_on_priority_change(self):
        self.member_state.member_characters.add(self.test_character)
        lower_state = State.objects.create(
            name='Lower State',
            priority=125,
        )
        lower_state.member_characters.add(self.test_character)
        self._refresh_user()
        lower_state.priority = 500
        lower_state.save()
        self._refresh_user()
        self.assertEquals(lower_state, self.user.profile.state)
        lower_state.priority = 125
        lower_state.save()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)

    def test_state_assignment_on_state_deletion(self):
        self.member_state.member_characters.add(self.test_character)
        higher_state = State.objects.create(
            name='Higher State',
            priority=200,
        )
        higher_state.member_characters.add(self.test_character)
        self._refresh_user()
        self.assertEquals(higher_state, self.user.profile.state)
        higher_state.delete()
        self.assertFalse(State.objects.filter(name='Higher State').count())
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)

    def test_state_assignment_on_public_toggle(self):
        self.member_state.member_characters.add(self.test_character)
        higher_state = State.objects.create(
            name='Higher State',
            priority=200,
        )
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)
        higher_state.public = True
        higher_state.save()
        self._refresh_user()
        self.assertEquals(higher_state, self.user.profile.state)
        higher_state.public = False
        higher_state.save()
        self._refresh_user()
        self.assertEquals(self.member_state, self.user.profile.state)

    def test_state_assignment_on_active_changed(self):
        self.member_state.member_characters.add(self.test_character)
        self.user.is_active = False
        self.user.save()
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.guest_state)
        self.user.is_active = True
        self.user.save()
        self._refresh_user()
        self.assertEquals(self.user.profile.state, self.member_state)


class CharacterOwnershipCheckTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('test_user', disconnect_signals=True)
        AuthUtils.add_main_character(cls.user, 'Test Character', '1', corp_id='1', alliance_id='1',
                                     corp_name='Test Corp', alliance_name='Test Alliance')
        cls.character = EveCharacter.objects.get(character_id='1')
        cls.token = Token.objects.create(
            user=cls.user,
            character_id='1',
            character_name='Test',
            character_owner_hash='1',
        )
        cls.ownership = CharacterOwnership.objects.get(character=cls.character)

    @mock.patch(MODULE_PATH + '.tasks.Token.update_token_data')
    def test_no_change_owner_hash(self, update_token_data):
        # makes sure the ownership isn't delete if owner hash hasn't changed
        check_character_ownership(self.ownership)
        self.assertTrue(CharacterOwnership.objects.filter(user=self.user).filter(character=self.character).exists())

    @mock.patch(MODULE_PATH + '.tasks.Token.update_token_data')
    def test_unable_to_update_token_data(self, update_token_data):
        # makes sure ownerships and tokens aren't hellpurged when there's problems with the SSO servers
        update_token_data.side_effect = IncompleteResponseError()
        check_character_ownership(self.ownership)
        self.assertTrue(CharacterOwnership.objects.filter(user=self.user).filter(character=self.character).exists())

        update_token_data.side_effect = KeyError()
        check_character_ownership(self.ownership)
        self.assertTrue(CharacterOwnership.objects.filter(user=self.user).filter(character=self.character).exists())

    @mock.patch(MODULE_PATH + '.tasks.Token.update_token_data')
    @mock.patch(MODULE_PATH + '.tasks.Token.delete')
    @mock.patch(MODULE_PATH + '.tasks.Token.objects.exists')
    @mock.patch(MODULE_PATH + '.tasks.CharacterOwnership.objects.filter')
    def test_owner_hash_changed(self, filter, exists, delete, update_token_data):
        # makes sure the ownership is revoked when owner hash changes
        filter.return_value.exists.return_value = False
        check_character_ownership(self.ownership)
        self.assertTrue(filter.return_value.delete.called)


class ManagementCommandTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('test user', disconnect_signals=True)
        AuthUtils.add_main_character(cls.user, 'test character', '1', '2', 'test corp', 'test')
        character = UserProfile.objects.get(user=cls.user).main_character
        CharacterOwnership.objects.create(user=cls.user, character=character, owner_hash='test')

    def setUp(self):
        self.stdout = StringIO()

    def test_ownership(self):
        call_command('checkmains', stdout=self.stdout)
        self.assertFalse(UserProfile.objects.filter(main_character__isnull=True).count())
        self.assertNotIn(self.user.username, self.stdout.getvalue())
        self.assertIn('All main characters', self.stdout.getvalue())

    def test_no_ownership(self):
        user = AuthUtils.create_user('v1 user', disconnect_signals=True)
        AuthUtils.add_main_character(user, 'v1 character', '10', '20', 'test corp', 'test')
        self.assertFalse(UserProfile.objects.filter(main_character__isnull=True).count())

        call_command('checkmains', stdout=self.stdout)
        self.assertEqual(UserProfile.objects.filter(main_character__isnull=True).count(), 1)
        self.assertIn(user.username, self.stdout.getvalue())
