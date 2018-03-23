from django.test import TestCase
from allianceauth.tests.auth_utils import AuthUtils

from ..models import AutogroupsConfig
from . import patch


class AutogroupsConfigManagerTestCase(TestCase):

    def test_update_groups_for_state(self):
        member = AuthUtils.create_member('test member')
        obj = AutogroupsConfig.objects.create()
        obj.states.add(member.profile.state)

        with patch('.models.AutogroupsConfig.update_group_membership_for_user') as update_group_membership_for_user:
            AutogroupsConfig.objects.update_groups_for_state(member.profile.state)

            self.assertTrue(update_group_membership_for_user.called)
            self.assertEqual(update_group_membership_for_user.call_count, 1)
            args, kwargs = update_group_membership_for_user.call_args
            self.assertEqual(args[0], member)

    def test_update_groups_for_user(self):
        member = AuthUtils.create_member('test member')
        obj = AutogroupsConfig.objects.create()
        obj.states.add(member.profile.state)

        with patch('.models.AutogroupsConfig.update_group_membership_for_user') as update_group_membership_for_user:
            AutogroupsConfig.objects.update_groups_for_user(member)

            self.assertTrue(update_group_membership_for_user.called)
            self.assertEqual(update_group_membership_for_user.call_count, 1)
            args, kwargs = update_group_membership_for_user.call_args
            self.assertEqual(args[0], member)

    @patch('.models.AutogroupsConfig.update_group_membership_for_user')
    @patch('.models.AutogroupsConfig.remove_user_from_alliance_groups')
    @patch('.models.AutogroupsConfig.remove_user_from_corp_groups')
    def test_update_groups_no_config(self, remove_corp, remove_alliance, update_groups):
        member = AuthUtils.create_member('test member')
        obj = AutogroupsConfig.objects.create()

        # Corp and alliance groups should be removed from users if their state has no config
        AutogroupsConfig.objects.update_groups_for_user(member)

        self.assertFalse(update_groups.called)
        self.assertTrue(remove_alliance.called)
        self.assertTrue(remove_corp.called)

        # The normal group assignment should occur if there state has a config
        obj.states.add(member.profile.state)
        AutogroupsConfig.objects.update_groups_for_user(member)

        self.assertTrue(update_groups.called)
