from django.test import TestCase
from django.contrib.auth.models import Group

from allianceauth.tests.auth_utils import AuthUtils

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo

from ..models import AutogroupsConfig, get_users_for_state


from . import patch, connect_signals, disconnect_signals


class AutogroupsConfigTestCase(TestCase):
    def setUp(self):
        # Disconnect signals
        disconnect_signals()

        state = AuthUtils.get_member_state()

        self.alliance = EveAllianceInfo.objects.create(
            alliance_id='3456',
            alliance_name='alliance name',
            alliance_ticker='TIKR',
            executor_corp_id='2345',
        )

        self.corp = EveCorporationInfo.objects.create(
            corporation_id='2345',
            corporation_name='corp name',
            corporation_ticker='TIKK',
            member_count=10,
            alliance=self.alliance,
        )

        state.member_alliances.add(self.alliance)
        state.member_corporations.add(self.corp)

        self.member = AuthUtils.create_member('test user')

    def tearDown(self):
        # Reconnect signals
        connect_signals()

    def test_get_users_for_state(self):
        result = get_users_for_state(self.member.profile.state)

        self.assertIn(self.member, result)
        self.assertEqual(len(result), 1)

    @patch('.models.AutogroupsConfig.update_alliance_group_membership')
    @patch('.models.AutogroupsConfig.update_corp_group_membership')
    def test_update_group_membership(self, update_corp, update_alliance):
        agc = AutogroupsConfig.objects.create()
        agc.update_group_membership_for_user(self.member)

        self.assertTrue(update_corp.called)
        self.assertTrue(update_alliance.called)

        args, kwargs = update_corp.call_args
        self.assertEqual(args[0], self.member)

        args, kwargs = update_alliance.call_args
        self.assertEqual(args[0], self.member)

    def test_update_alliance_group_membership(self):
        obj = AutogroupsConfig.objects.create(alliance_groups=True)
        obj.states.add(AuthUtils.get_member_state())
        char = EveCharacter.objects.create(
            character_id='1234',
            character_name='test character',
            corporation_id='2345',
            corporation_name='test corp',
            corporation_ticker='tickr',
            alliance_id='3456',
            alliance_name='alliance name',
        )
        self.member.profile.main_character = char
        self.member.profile.save()

        pre_groups = self.member.groups.all()

        # Act
        obj.update_alliance_group_membership(self.member)
        obj.update_corp_group_membership(self.member)  # check for no side effects

        group = obj.create_alliance_group(self.alliance)
        group_qs = Group.objects.filter(pk=group.pk)

        self.assertIn(group, self.member.groups.all())
        self.assertQuerysetEqual(self.member.groups.all(), map(repr, pre_groups | group_qs), ordered=False)

    def test_update_alliance_group_membership_no_main_character(self):
        obj = AutogroupsConfig.objects.create()
        obj.states.add(AuthUtils.get_member_state())

        # Act
        obj.update_alliance_group_membership(self.member)

        group = obj.get_alliance_group(self.alliance)

        self.assertNotIn(group, self.member.groups.all())

    def test_update_alliance_group_membership_no_alliance_model(self):
        obj = AutogroupsConfig.objects.create()
        obj.states.add(AuthUtils.get_member_state())
        char = EveCharacter.objects.create(
            character_id='1234',
            character_name='test character',
            corporation_id='2345',
            corporation_name='test corp',
            corporation_ticker='tickr',
            alliance_id='3459',
            alliance_name='alliance name',
        )
        self.member.profile.main_character = char
        self.member.profile.save()

        # Act
        obj.update_alliance_group_membership(self.member)

        group = obj.get_alliance_group(self.alliance)

        self.assertNotIn(group, self.member.groups.all())

    def test_update_corp_group_membership(self):
        obj = AutogroupsConfig.objects.create(corp_groups=True)
        obj.states.add(AuthUtils.get_member_state())
        char = EveCharacter.objects.create(
            character_id='1234',
            character_name='test character',
            corporation_id='2345',
            corporation_name='test corp',
            corporation_ticker='tickr',
            alliance_id='3456',
            alliance_name='alliance name',
        )
        self.member.profile.main_character = char
        self.member.profile.save()

        pre_groups = self.member.groups.all()

        # Act
        obj.update_corp_group_membership(self.member)

        group = obj.get_corp_group(self.corp)
        group_qs = Group.objects.filter(pk=group.pk)

        self.assertIn(group, self.member.groups.all())
        self.assertQuerysetEqual(self.member.groups.all(), map(repr, pre_groups | group_qs), ordered=False)

    def test_update_corp_group_membership_no_state(self):
        obj = AutogroupsConfig.objects.create(corp_groups=True)
        char = EveCharacter.objects.create(
            character_id='1234',
            character_name='test character',
            corporation_id='2345',
            corporation_name='test corp',
            corporation_ticker='tickr',
            alliance_id='3456',
            alliance_name='alliance name',
        )
        self.member.profile.main_character = char
        self.member.profile.save()

        pre_groups = list(self.member.groups.all())

        # Act
        obj.update_corp_group_membership(self.member)

        group = obj.get_corp_group(self.corp)

        post_groups = list(self.member.groups.all())

        self.assertNotIn(group, post_groups)
        self.assertListEqual(pre_groups, post_groups)

    def test_update_corp_group_membership_no_main_character(self):
        obj = AutogroupsConfig.objects.create()
        obj.states.add(AuthUtils.get_member_state())

        # Act
        obj.update_corp_group_membership(self.member)

        group = obj.get_corp_group(self.corp)

        self.assertNotIn(group, self.member.groups.all())

    def test_update_corp_group_membership_no_corp_model(self):
        obj = AutogroupsConfig.objects.create()
        obj.states.add(AuthUtils.get_member_state())
        char = EveCharacter.objects.create(
            character_id='1234',
            character_name='test character',
            corporation_id='2348',
            corporation_name='test corp',
            corporation_ticker='tickr',
            alliance_id='3456',
            alliance_name='alliance name',
        )
        self.member.profile.main_character = char
        self.member.profile.save()

        # Act
        obj.update_corp_group_membership(self.member)

        group = obj.get_corp_group(self.corp)

        self.assertNotIn(group, self.member.groups.all())

    def test_remove_user_from_alliance_groups(self):
        obj = AutogroupsConfig.objects.create()
        result = obj.get_alliance_group(self.alliance)

        result.user_set.add(self.member)

        self.assertIn(result, self.member.groups.all())

        # Act
        obj.remove_user_from_alliance_groups(self.member)

        self.assertNotIn(result, self.member.groups.all())

    def test_remove_user_from_corp_groups(self):
        obj = AutogroupsConfig.objects.create()
        result = obj.get_corp_group(self.corp)

        result.user_set.add(self.member)

        self.assertIn(result, self.member.groups.all())

        # Act
        obj.remove_user_from_corp_groups(self.member)

        self.assertNotIn(result, self.member.groups.all())

    def test_get_alliance_group(self):
        obj = AutogroupsConfig.objects.create()
        result = obj.get_alliance_group(self.alliance)

        group = Group.objects.get(name='Alliance alliance name')

        self.assertEqual(result, group)
        self.assertEqual(obj.get_alliance_group_name(self.alliance), result.name)
        self.assertTrue(obj.alliance_managed_groups.filter(pk=result.pk).exists())

    def test_get_corp_group(self):
        obj = AutogroupsConfig.objects.create()
        result = obj.get_corp_group(self.corp)

        group = Group.objects.get(name='Corp corp name')

        self.assertEqual(result, group)
        self.assertEqual(obj.get_corp_group_name(self.corp), group.name)
        self.assertTrue(obj.corp_managed_groups.filter(pk=group.pk).exists())

    def test_create_alliance_group(self):
        obj = AutogroupsConfig.objects.create()
        result = obj.create_alliance_group(self.alliance)

        group = Group.objects.get(name='Alliance alliance name')

        self.assertEqual(result, group)
        self.assertEqual(obj.get_alliance_group_name(self.alliance), group.name)
        self.assertTrue(obj.alliance_managed_groups.filter(pk=group.pk).exists())

    def test_create_corp_group(self):
        obj = AutogroupsConfig.objects.create()
        result = obj.create_corp_group(self.corp)

        group = Group.objects.get(name='Corp corp name')

        self.assertEqual(result, group)
        self.assertEqual(obj.get_corp_group_name(self.corp), group.name)
        self.assertTrue(obj.corp_managed_groups.filter(pk=group.pk).exists())

    def test_delete_alliance_managed_groups(self):
        obj = AutogroupsConfig.objects.create()
        obj.create_alliance_group(self.alliance)

        self.assertTrue(obj.alliance_managed_groups.all().exists())

        obj.delete_alliance_managed_groups()

        self.assertFalse(obj.alliance_managed_groups.all().exists())

    def test_delete_corp_managed_groups(self):
        obj = AutogroupsConfig.objects.create()
        obj.create_corp_group(self.corp)

        self.assertTrue(obj.corp_managed_groups.all().exists())

        obj.delete_corp_managed_groups()

        self.assertFalse(obj.corp_managed_groups.all().exists())

    def test_get_alliance_group_name(self):
        obj = AutogroupsConfig()
        obj.replace_spaces = True
        obj.replace_spaces_with = '_'

        result = obj.get_alliance_group_name(self.alliance)

        self.assertEqual(result, 'Alliance_alliance_name')

    def test_get_alliance_group_name_ticker(self):
        obj = AutogroupsConfig()
        obj.replace_spaces = True
        obj.replace_spaces_with = '_'
        obj.alliance_name_source = obj.OPT_TICKER

        result = obj.get_alliance_group_name(self.alliance)

        self.assertEqual(result, 'Alliance_TIKR')

    def test_get_corp_group_name(self):
        obj = AutogroupsConfig()
        obj.replace_spaces = True
        obj.replace_spaces_with = '_'

        result = obj.get_corp_group_name(self.corp)

        self.assertEqual(result, 'Corp_corp_name')

    def test_get_corp_group_name_ticker(self):
        obj = AutogroupsConfig()
        obj.replace_spaces = True
        obj.replace_spaces_with = '_'
        obj.corp_name_source = obj.OPT_TICKER

        result = obj.get_corp_group_name(self.corp)

        self.assertEqual(result, 'Corp_TIKK')

    def test__replace_spaces(self):
        obj = AutogroupsConfig()
        obj.replace_spaces = True
        obj.replace_spaces_with = '*'
        name = ' test name '

        result = obj._replace_spaces(name)

        self.assertEqual(result, 'test*name')
