from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase
from django.contrib.auth.models import Group, Permission

from alliance_auth.tests.auth_utils import AuthUtils


class ServicesSignalsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.none_user = AuthUtils.create_user('none_user', disconnect_signals=True)

    @mock.patch('services.signals.transaction')
    @mock.patch('services.signals.ServicesHook')
    def test_m2m_changed_user_groups(self, services_hook, transaction):
        """
        Test that update_groups hook function is called on user groups change
        """
        svc = mock.Mock()
        svc.update_groups.return_value = None
        svc.validate_user.return_value = None

        services_hook.get_services.return_value = [svc]

        # Overload transaction.on_commit so everything happens synchronously
        transaction.on_commit = lambda fn: fn()

        test_group = Group.objects.create(name="Test group")

        # Act, should trigger m2m change
        self.member.groups.add(test_group)
        self.member.save()

        # Assert
        self.assertTrue(services_hook.get_services.called)

        self.assertTrue(svc.update_groups.called)
        args, kwargs = svc.update_groups.call_args
        self.assertEqual(self.member, args[0])

        self.assertTrue(svc.validate_user.called)
        args, kwargs = svc.validate_user.call_args
        self.assertEqual(self.member, args[0])

    
    @mock.patch('services.signals.disable_user')
    def test_pre_delete_user(self, disable_user):

        """
        Test that disable_member is called when a user is deleted
        """
        self.none_user.delete()

        self.assertTrue(disable_user.called)
        args, kwargs = disable_user.call_args
        self.assertEqual(self.none_user, args[0])

    @mock.patch('services.signals.disable_user')
    def test_pre_save_user_inactivation(self, disable_user):
        """
        Test a user set inactive has disable_member called
        """
        self.member.is_active = False
        self.member.save()  # Signal Trigger

        self.assertTrue(disable_user.called)
        args, kwargs = disable_user.call_args
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

    @mock.patch('services.signals.transaction')
    @mock.patch('services.signals.ServicesHook')
    def test_m2m_changed_group_permissions(self, services_hook, transaction):
        from django.contrib.contenttypes.models import ContentType
        svc = mock.Mock()
        svc.validate_user.return_value = None
        svc.access_perm = 'auth.access_testsvc'

        services_hook.get_services.return_value = [svc]

        # Overload transaction.on_commit so everything happens synchronously
        transaction.on_commit = lambda fn: fn()

        test_group = Group.objects.create(name="Test group")
        AuthUtils.disconnect_signals()
        self.member.groups.add(test_group)
        AuthUtils.connect_signals()

        ct = ContentType.objects.get(app_label='auth', model='permission')
        perm = Permission.objects.create(name="Test perm", codename="access_testsvc", content_type=ct)
        test_group.permissions.add(perm)

        # Act, should trigger m2m change
        test_group.permissions.remove(perm)

        # Assert
        self.assertTrue(services_hook.get_services.called)

        self.assertTrue(svc.validate_user.called)
        args, kwargs = svc.validate_user.call_args
        self.assertEqual(self.member, args[0])

    @mock.patch('services.signals.transaction')
    @mock.patch('services.signals.ServicesHook')
    def test_m2m_changed_user_permissions(self, services_hook, transaction):
        from django.contrib.contenttypes.models import ContentType
        svc = mock.Mock()
        svc.validate_user.return_value = None
        svc.access_perm = 'auth.access_testsvc'

        services_hook.get_services.return_value = [svc]

        # Overload transaction.on_commit so everything happens synchronously
        transaction.on_commit = lambda fn: fn()

        ct = ContentType.objects.get(app_label='auth', model='permission')
        perm = Permission.objects.create(name="Test perm", codename="access_testsvc", content_type=ct)
        self.member.user_permissions.add(perm)

        # Act, should trigger m2m change
        self.member.user_permissions.remove(perm)

        # Assert
        self.assertTrue(services_hook.get_services.called)

        self.assertTrue(svc.validate_user.called)
        args, kwargs = svc.validate_user.call_args
        self.assertEqual(self.member, args[0])
