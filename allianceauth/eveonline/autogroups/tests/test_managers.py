from django.test import TestCase
from allianceauth.tests.auth_utils import AuthUtils

from ..models import AutogroupsConfig
from . import patch


class AutogroupsConfigManagerTestCase(TestCase):

    def test_update_groups_for_state(self, ):
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
