from unittest import mock

from django.test import TestCase
from allianceauth.tests.auth_utils import AuthUtils
from .models import CorpStats, CorpMember
from allianceauth.eveonline.models import EveCorporationInfo, EveAllianceInfo, EveCharacter
from esi.models import Token
from esi.errors import TokenError
from bravado.exception import HTTPForbidden
from django.contrib.auth.models import Permission
from allianceauth.authentication.models import CharacterOwnership


class CorpStatsManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('test')
        AuthUtils.add_main_character(cls.user, 'test character', '1', corp_id='2', corp_name='test_corp', corp_ticker='TEST', alliance_id='3', alliance_name='TEST')
        cls.user.profile.refresh_from_db()
        cls.alliance = EveAllianceInfo.objects.create(alliance_id='3', alliance_name='test alliance', alliance_ticker='TEST', executor_corp_id='2')
        cls.corp = EveCorporationInfo.objects.create(corporation_id='2', corporation_name='test corp', corporation_ticker='TEST', alliance=cls.alliance, member_count=1)
        cls.token = Token.objects.create(user=cls.user, access_token='a', character_id='1', character_name='test character', character_owner_hash='z')
        cls.corpstats = CorpStats.objects.create(corp=cls.corp, token=cls.token)
        cls.view_corp_permission = Permission.objects.get_by_natural_key('view_corp_corpstats', 'corputils', 'corpstats')
        cls.view_alliance_permission = Permission.objects.get_by_natural_key('view_alliance_corpstats', 'corputils', 'corpstats')
        cls.view_state_permission = Permission.objects.get_by_natural_key('view_state_corpstats', 'corputils', 'corpstats')
        cls.state = AuthUtils.create_state('test state', 500)
        AuthUtils.assign_state(cls.user, cls.state, disconnect_signals=True)

    def setUp(self):
        self.user.refresh_from_db()
        self.user.user_permissions.clear()
        self.state.refresh_from_db()
        self.state.member_corporations.clear()
        self.state.member_alliances.clear()

    def test_visible_superuser(self):
        self.user.is_superuser = True
        cs = CorpStats.objects.visible_to(self.user)
        self.assertIn(self.corpstats, cs)

    def test_visible_corporation(self):
        self.user.user_permissions.add(self.view_corp_permission)
        cs = CorpStats.objects.visible_to(self.user)
        self.assertIn(self.corpstats, cs)

    def test_visible_alliance(self):
        self.user.user_permissions.add(self.view_alliance_permission)
        cs = CorpStats.objects.visible_to(self.user)
        self.assertIn(self.corpstats, cs)

    def test_visible_state_corp_member(self):
        self.state.member_corporations.add(self.corp)
        self.user.user_permissions.add(self.view_state_permission)
        cs = CorpStats.objects.visible_to(self.user)
        self.assertIn(self.corpstats, cs)

    def test_visible_state_alliance_member(self):
        self.state.member_alliances.add(self.alliance)
        self.user.user_permissions.add(self.view_state_permission)
        cs = CorpStats.objects.visible_to(self.user)
        self.assertIn(self.corpstats, cs)


class CorpStatsUpdateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('test')
        AuthUtils.add_main_character(cls.user, 'test character', '1', corp_id='2', corp_name='test_corp', corp_ticker='TEST', alliance_id='3', alliance_name='TEST')
        cls.token = Token.objects.create(user=cls.user, access_token='a', character_id='1', character_name='test character', character_owner_hash='z')
        cls.corp = EveCorporationInfo.objects.create(corporation_id='2', corporation_name='test corp', corporation_ticker='TEST', member_count=1)

    def setUp(self):
        self.corpstats = CorpStats.objects.get_or_create(token=self.token, corp=self.corp)[0]

    def test_can_update(self):
        self.assertTrue(self.corpstats.can_update(self.user))
        self.corpstats.token.user = None
        self.assertFalse(self.corpstats.can_update(self.user))
        self.user.is_superuser = True
        self.assertTrue(self.corpstats.can_update(self.user))
        self.user.refresh_from_db()
        self.corpstats.token.refresh_from_db()

    @mock.patch('esi.clients.SwaggerClient')
    def test_update_add_member(self, SwaggerClient):
        SwaggerClient.from_spec.return_value.Character.get_characters_character_id.return_value.result.return_value = {'corporation_id': 2}
        SwaggerClient.from_spec.return_value.Corporation.get_corporations_corporation_id_members.return_value.result.return_value = [1]
        SwaggerClient.from_spec.return_value.Character.get_characters_names.return_value.result.return_value = [{'character_id': 1, 'character_name': 'test character'}]
        self.corpstats.update()
        self.assertTrue(CorpMember.objects.filter(character_id='1', character_name='test character', corpstats=self.corpstats).exists())

    @mock.patch('esi.clients.SwaggerClient')
    def test_update_remove_member(self, SwaggerClient):
        CorpMember.objects.create(character_id='2', character_name='old test character', corpstats=self.corpstats)
        SwaggerClient.from_spec.return_value.Character.get_characters_character_id.return_value.result.return_value = {'corporation_id': 2}
        SwaggerClient.from_spec.return_value.Corporation.get_corporations_corporation_id_members.return_value.result.return_value = [1]
        SwaggerClient.from_spec.return_value.Character.get_characters_names.return_value.result.return_value = [{'character_id': 1, 'character_name': 'test character'}]
        self.corpstats.update()
        self.assertFalse(CorpMember.objects.filter(character_id='2', corpstats=self.corpstats).exists())

    @mock.patch('allianceauth.corputils.models.notify')
    @mock.patch('esi.clients.SwaggerClient')
    def test_update_deleted_token(self, SwaggerClient, notify):
        SwaggerClient.from_spec.return_value.Character.get_characters_character_id.return_value.result.return_value = {'corporation_id': 2}
        SwaggerClient.from_spec.return_value.Corporation.get_corporations_corporation_id_members.return_value.result.side_effect = TokenError()
        self.corpstats.update()
        self.assertFalse(CorpStats.objects.filter(corp=self.corp).exists())
        self.assertTrue(notify.called)

    @mock.patch('allianceauth.corputils.models.notify')
    @mock.patch('esi.clients.SwaggerClient')
    def test_update_http_forbidden(self, SwaggerClient, notify):
        SwaggerClient.from_spec.return_value.Character.get_characters_character_id.return_value.result.return_value = {'corporation_id': 2}
        SwaggerClient.from_spec.return_value.Corporation.get_corporations_corporation_id_members.return_value.result.side_effect = HTTPForbidden(mock.Mock())
        self.corpstats.update()
        self.assertFalse(CorpStats.objects.filter(corp=self.corp).exists())
        self.assertTrue(notify.called)

    @mock.patch('allianceauth.corputils.models.notify')
    @mock.patch('esi.clients.SwaggerClient')
    def test_update_token_character_corp_changed(self, SwaggerClient, notify):
        SwaggerClient.from_spec.return_value.Character.get_characters_character_id.return_value.result.return_value = {'corporation_id': 3}
        self.corpstats.update()
        self.assertFalse(CorpStats.objects.filter(corp=self.corp).exists())
        self.assertTrue(notify.called)


class CorpStatsPropertiesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('test')
        AuthUtils.add_main_character(cls.user, 'test character', '1', corp_id='2', corp_name='test_corp', corp_ticker='TEST', alliance_id='3', alliance_name='TEST')
        cls.user.profile.refresh_from_db()
        cls.token = Token.objects.create(user=cls.user, access_token='a', character_id='1', character_name='test character', character_owner_hash='z')
        cls.corp = EveCorporationInfo.objects.create(corporation_id='2', corporation_name='test corp', corporation_ticker='TEST', member_count=1)
        cls.corpstats = CorpStats.objects.create(token=cls.token, corp=cls.corp)
        cls.character = EveCharacter.objects.create(character_name='another test character', character_id='4', corporation_id='2', corporation_name='test corp', corporation_ticker='TEST')

    def test_member_count(self):
        member = CorpMember.objects.create(corpstats=self.corpstats, character_id='1', character_name='test character')
        self.assertEqual(self.corpstats.member_count, 1)
        member.delete()
        self.assertEqual(self.corpstats.member_count, 0)

    def test_user_count(self):
        AuthUtils.disconnect_signals()
        co = CharacterOwnership.objects.create(character=self.character, user=self.user, owner_hash='a')
        AuthUtils.connect_signals()
        CorpMember.objects.create(corpstats=self.corpstats, character_id='4', character_name='test character')
        self.assertEqual(self.corpstats.user_count, 1)
        co.delete()
        self.assertEqual(self.corpstats.user_count, 0)

    def test_registered_members(self):
        AuthUtils.disconnect_signals()
        co = CharacterOwnership.objects.create(character=self.character, user=self.user, owner_hash='a')
        AuthUtils.connect_signals()
        member = CorpMember.objects.create(corpstats=self.corpstats, character_id='4', character_name='test character')
        self.assertIn(member, self.corpstats.registered_members)
        self.assertEqual(self.corpstats.registered_member_count, 1)

        co.delete()
        self.assertNotIn(member, self.corpstats.registered_members)
        self.assertEqual(self.corpstats.registered_member_count, 0)

    def test_unregistered_members(self):
        member = CorpMember.objects.create(corpstats=self.corpstats, character_id='4', character_name='test character')
        self.corpstats.refresh_from_db()
        self.assertIn(member, self.corpstats.unregistered_members)
        self.assertEqual(self.corpstats.unregistered_member_count, 1)

        AuthUtils.disconnect_signals()
        CharacterOwnership.objects.create(character=self.character, user=self.user, owner_hash='a')
        AuthUtils.connect_signals()
        self.assertNotIn(member, self.corpstats.unregistered_members)
        self.assertEqual(self.corpstats.unregistered_member_count, 0)

    def test_mains(self):
        # test when is a main
        member = CorpMember.objects.create(corpstats=self.corpstats, character_id='1', character_name='test character')
        self.assertIn(member, self.corpstats.mains)
        self.assertEqual(self.corpstats.main_count, 1)

        # test when is an alt
        old_main = self.user.profile.main_character
        character = EveCharacter.objects.create(character_name='other character', character_id=10, corporation_name='test corp', corporation_id='2', corporation_ticker='TEST')
        AuthUtils.disconnect_signals()
        co = CharacterOwnership.objects.create(character=character, user=self.user, owner_hash='b')
        self.user.profile.main_character = character
        self.user.profile.save()
        AuthUtils.connect_signals()
        self.assertNotIn(member, self.corpstats.mains)
        self.assertEqual(self.corpstats.main_count, 0)

        # test when no ownership
        co.delete()
        self.assertNotIn(member, self.corpstats.mains)
        self.assertEqual(self.corpstats.main_count, 0)

        # transaction won't roll this back
        AuthUtils.disconnect_signals()
        self.user.profile.main_character = old_main
        self.user.profile.save()
        AuthUtils.connect_signals()

    def test_logos(self):
        self.assertEqual(self.corpstats.corp_logo(size=128), 'https://image.eveonline.com/Corporation/2_128.png')
        self.assertEqual(self.corpstats.alliance_logo(size=128), 'https://image.eveonline.com/Alliance/1_128.png')

        alliance = EveAllianceInfo.objects.create(alliance_name='test alliance', alliance_id='3', alliance_ticker='TEST', executor_corp_id='2')
        self.corp.alliance = alliance
        self.corp.save()
        self.assertEqual(self.corpstats.alliance_logo(size=128), 'https://image.eveonline.com/Alliance/3_128.png')
        alliance.delete()


class CorpMemberTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('test')
        AuthUtils.add_main_character(cls.user, 'test character', '1', corp_id='2', corp_name='test_corp', corp_ticker='TEST', alliance_id='3', alliance_name='TEST')
        cls.user.profile.refresh_from_db()
        cls.token = Token.objects.create(user=cls.user, access_token='a', character_id='1', character_name='test character', character_owner_hash='a')
        cls.corp = EveCorporationInfo.objects.create(corporation_id='2', corporation_name='test corp', corporation_ticker='TEST', member_count=1)
        cls.corpstats = CorpStats.objects.create(token=cls.token, corp=cls.corp)
        cls.member = CorpMember.objects.create(corpstats=cls.corpstats, character_id='2', character_name='other test character')

    def test_character(self):
        self.assertIsNone(self.member.character)
        character = EveCharacter.objects.create(character_id='2', character_name='other test character', corporation_id='2', corporation_name='test corp', corporation_ticker='TEST')
        self.assertEqual(self.member.character, character)

    def test_main_character(self):
        AuthUtils.disconnect_signals()

        # test when member.character is None
        self.assertIsNone(self.member.main_character)

        # test when member.character is not None but also not a main
        character = EveCharacter.objects.create(character_id='2', character_name='other test character', corporation_id='2', corporation_name='test corp', corporation_ticker='TEST')
        CharacterOwnership.objects.create(character=character, user=self.user, owner_hash='b')
        self.member.refresh_from_db()
        self.assertNotEqual(self.member.main_character, self.member.character)
        self.assertEquals(self.member.main_character, self.user.profile.main_character)

        # test when is main
        old_main = self.user.profile.main_character
        self.user.profile.main_character = character
        self.user.profile.save()
        self.member.refresh_from_db()
        self.assertEqual(self.member.main_character, self.member.character)
        self.assertEqual(self.user.profile.main_character, self.member.main_character)

        # transaction won't roll this back
        self.user.profile.main_character = old_main
        self.user.profile.save()
        AuthUtils.connect_signals()

    def test_alts(self):
        self.assertListEqual(self.member.alts, [])

        character = EveCharacter.objects.create(character_id='2', character_name='other test character', corporation_id='2', corporation_name='test corp', corporation_ticker='TEST')
        CharacterOwnership.objects.create(character=character, user=self.user, owner_hash='b')
        self.assertIn(character, self.member.alts)

    def test_registered(self):
        self.assertFalse(self.member.registered)
        AuthUtils.disconnect_signals()
        character = EveCharacter.objects.create(character_id='2', character_name='other test character', corporation_id='2', corporation_name='test corp', corporation_ticker='TEST')
        CharacterOwnership.objects.create(character=character, user=self.user, owner_hash='b')
        self.assertTrue(self.member.registered)
        AuthUtils.connect_signals()

    def test_portrait_url(self):
        self.assertEquals(self.member.portrait_url(size=32), 'https://image.eveonline.com/Character/2_32.jpg')
        self.assertEquals(self.member.portrait_url(size=32), self.member.portrait_url_32)
