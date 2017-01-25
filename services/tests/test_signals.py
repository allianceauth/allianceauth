from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase
from django.contrib.auth.models import Group

from alliance_auth.tests.auth_utils import AuthUtils


class ServicesSignalsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.none_user = AuthUtils.create_user('none_user', disconnect_signals=True)

    @mock.patch('services.signals.transaction')
    @mock.patch('services.signals.get_hooks')
    def test_m2m_changed_user_groups(self, get_hooks, transaction):
        """
        Test that update_groups hook function is called on user groups change
        """
        svc = mock.Mock()
        svc.update_groups.return_value = None

        get_hooks.return_value = [lambda: svc]

        # Overload transaction.on_commit so everything happens synchronously
        transaction.on_commit = lambda fn: fn()

        test_group = Group.objects.create(name="Test group")

        # Act, should trigger m2m change
        self.member.groups.add(test_group)
        self.member.save()

        # Assert
        self.assertTrue(get_hooks.called)
        args, kwargs = get_hooks.call_args
        self.assertEqual('services_hook', args[0])

        self.assertTrue(svc.update_groups.called)
        args, kwargs = svc.update_groups.call_args
        self.assertEqual(self.member, args[0])

    @mock.patch('services.signals.disable_member')
    def test_pre_delete_user(self, disable_member):
        """
        Test that disable_member is called when a user is deleted
        """
        self.none_user.delete()

        self.assertTrue(disable_member.called)
        args, kwargs = disable_member.call_args
        self.assertEqual(self.none_user, args[0])

    @mock.patch('services.signals.disable_member')
    def test_pre_save_user_inactivation(self, disable_member):
        """
        Test a user set inactive has disable_member called
        """
        self.member.is_active = False
        self.member.save()  # Signal Trigger

        self.assertTrue(disable_member.called)
        args, kwargs = disable_member.call_args
        self.assertEqual(self.member, args[0])

    @mock.patch('services.signals.set_state')
    def test_pre_save_user_activation(self, set_state):
        """
        Test a user set inactive has disable_member called
        """
        # Arrange, set user inactive first
        self.member.is_active = False
        self.member.save()  # Signal Trigger (but not the one we want)

        set_state.reset_mock()

        # Act
        self.member.is_active = True
        self.member.save()  # Signal Trigger

        # Assert
        self.assertTrue(set_state.called)
        args, kwargs = set_state.call_args
        self.assertEqual(self.member, args[0])
