from django.test import TestCase
from django.contrib.auth.models import User

from allianceauth.tests.auth_utils import AuthUtils

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo

from ..models import AutogroupsConfig

from . import patch, disconnect_signals, connect_signals


class SignalsTestCase(TestCase):
    def setUp(self):
        disconnect_signals()
        state = AuthUtils.get_member_state()

        self.char = EveCharacter.objects.create(
            character_id='1234',
            character_name='test character',
            corporation_id='2345',
            corporation_name='test corp',
            corporation_ticker='tickr',
            alliance_id='3456',
            alliance_name='alliance name',
        )

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
        self.member.profile.main_character = self.char
        self.member.profile.save()

        connect_signals()

    @patch('.models.AutogroupsConfigManager.update_groups_for_user')
    def test_check_groups_on_profile_update_state(self, update_groups_for_user):
        # Trigger signal
        self.member.profile.assign_state(state=AuthUtils.get_guest_state())

        self.assertTrue(update_groups_for_user.called)
        self.assertEqual(update_groups_for_user.call_count, 1)
        args, kwargs = update_groups_for_user.call_args
        self.assertEqual(args[0], self.member)

    @patch('.models.AutogroupsConfigManager.update_groups_for_user')
    def test_check_groups_on_profile_update_main_character(self, update_groups_for_user):
        char = EveCharacter.objects.create(
            character_id='1266',
            character_name='test character2',
            corporation_id='2345',
            corporation_name='test corp',
            corporation_ticker='tickr',
            alliance_id='3456',
            alliance_name='alliance name',
        )

        # Trigger signal
        self.member.profile.main_character = char
        self.member.profile.save()
        self.assertTrue(update_groups_for_user.called)
        self.assertEqual(update_groups_for_user.call_count, 1)
        args, kwargs = update_groups_for_user.call_args
        self.assertEqual(args[0], self.member)
        member = User.objects.get(pk=self.member.pk)
        self.assertEqual(member.profile.state, AuthUtils.get_member_state())

    @patch('.models.AutogroupsConfigManager.update_groups_for_user')
    def test_check_groups_on_character_update(self, update_groups_for_user):
        """
        Test update_groups_for_user is called when main_character properties
        are changed.
        """

        # Trigger signal
        self.member.profile.main_character.corporation_id = '2300'
        self.member.profile.main_character.save()

        self.assertTrue(update_groups_for_user.called)
        self.assertEqual(update_groups_for_user.call_count, 1)
        args, kwargs = update_groups_for_user.call_args
        self.assertEqual(args[0], self.member)
        member = User.objects.get(pk=self.member.pk)
        self.assertEqual(member.profile.state, AuthUtils.get_member_state())

    @patch('.models.AutogroupsConfig.delete_corp_managed_groups')
    @patch('.models.AutogroupsConfig.delete_alliance_managed_groups')
    def test_pre_save_config_deletes_alliance_groups(self, delete_alliance_managed_groups, delete_corp_managed_groups):
        """
        Test that delete_alliance_managed_groups is called when the alliance_groups
        setting is toggled to False
        """
        obj = AutogroupsConfig.objects.create(alliance_groups=True)

        obj.create_alliance_group(self.alliance)

        # Trigger signal
        obj.alliance_groups = False
        obj.save()

        self.assertTrue(delete_alliance_managed_groups.called)
        self.assertFalse(delete_corp_managed_groups.called)
        self.assertEqual(delete_alliance_managed_groups.call_count, 1)

    @patch('.models.AutogroupsConfig.delete_alliance_managed_groups')
    @patch('.models.AutogroupsConfig.delete_corp_managed_groups')
    def test_pre_save_config_deletes_corp_groups(self, delete_corp_managed_groups, delete_alliance_managed_groups):
        """
        Test that delete_corp_managed_groups is called when the corp_groups
        setting is toggled to False
        """
        obj = AutogroupsConfig.objects.create(corp_groups=True)

        obj.create_corp_group(self.corp)

        # Trigger signal
        obj.corp_groups = False
        obj.save()

        self.assertTrue(delete_corp_managed_groups.called)
        self.assertFalse(delete_alliance_managed_groups.called)
        self.assertEqual(delete_corp_managed_groups.call_count, 1)

    @patch('.models.AutogroupsConfig.delete_alliance_managed_groups')
    @patch('.models.AutogroupsConfig.delete_corp_managed_groups')
    def test_pre_save_config_does_nothing(self, delete_corp_managed_groups, delete_alliance_managed_groups):
        """
        Test groups arent deleted if we arent setting the enabled params to False
        """
        obj = AutogroupsConfig.objects.create(corp_groups=True)

        obj.create_corp_group(self.corp)

        # Trigger signal
        obj.alliance_groups = True
        obj.save()

        self.assertFalse(delete_corp_managed_groups.called)
        self.assertFalse(delete_alliance_managed_groups.called)

    @patch('.models.AutogroupsConfig.delete_alliance_managed_groups')
    @patch('.models.AutogroupsConfig.delete_corp_managed_groups')
    def test_pre_delete_config(self, delete_corp_managed_groups, delete_alliance_managed_groups):
        """
        Test groups are deleted if config is deleted
        """
        obj = AutogroupsConfig.objects.create()

        # Trigger signal
        obj.delete()

        self.assertTrue(delete_corp_managed_groups.called)
        self.assertTrue(delete_alliance_managed_groups.called)

    @patch('.models.AutogroupsConfig.update_group_membership_for_state')
    def test_autogroups_states_changed_add(self, update_group_membership_for_state):
        """
        Test update_group_membership_for_state is called when a state is added to
        the AutogroupsConfig
        """
        obj = AutogroupsConfig.objects.create(alliance_groups=True)
        state = AuthUtils.get_member_state()

        # Trigger
        obj.states.add(state)

        self.assertTrue(update_group_membership_for_state.called)
        self.assertEqual(update_group_membership_for_state.call_count, 1)
        args, kwargs = update_group_membership_for_state.call_args
        self.assertEqual(args[0], state)

    @patch('.models.AutogroupsConfig.update_group_membership_for_state')
    def test_autogroups_states_changed_remove(self, update_group_membership_for_state):
        """
        Test update_group_membership_for_state is called when a state is removed from
        the AutogroupsConfig
        """
        obj = AutogroupsConfig.objects.create(alliance_groups=True)
        state = AuthUtils.get_member_state()

        disconnect_signals()
        obj.states.add(state)
        connect_signals()

        # Trigger
        obj.states.remove(state)

        self.assertTrue(update_group_membership_for_state.called)
        self.assertEqual(update_group_membership_for_state.call_count, 1)
        args, kwargs = update_group_membership_for_state.call_args
        self.assertEqual(args[0], state)
