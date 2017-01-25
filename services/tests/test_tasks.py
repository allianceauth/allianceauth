from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase

from authentication.states import MEMBER_STATE, BLUE_STATE, NONE_STATE
from alliance_auth.tests.auth_utils import AuthUtils

from services.tasks import deactivate_services, validate_services


class ServicesTasksTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.none_user = AuthUtils.create_user('none_user', disconnect_signals=True)

    @mock.patch('services.tasks.get_hooks')
    @mock.patch('services.tasks.deactivate_services')
    def test_validate_services_deactivate(self, deactivate_services, get_hooks):
        """
        Test validate services will call deactivate on a None state user
        """

        validate_services.delay(user=self.none_user, state=NONE_STATE)

        self.assertTrue(deactivate_services.called)
        args, kwargs = deactivate_services.call_args
        self.assertEqual(self.none_user, args[0])  # Assert correct user is passed
        self.assertFalse(get_hooks.called)

    @mock.patch('services.tasks.get_hooks')
    @mock.patch('services.tasks.deactivate_services')
    def test_validate_services_valid_member(self, deactivate_services, get_hooks):
        """
        Test that validate_services is called for a valid member
        """
        svc = mock.Mock()
        svc.validate_user.return_value = None

        get_hooks.return_value = [lambda: svc]

        validate_services.delay(user=self.member, state=MEMBER_STATE)

        self.assertTrue(get_hooks.called)
        args, kwargs = get_hooks.call_args
        self.assertEqual('services_hook', args[0])
        self.assertTrue(svc.validate_user.called)
        args, kwargs = svc.validate_user.call_args
        self.assertEqual(self.member, args[0])  # Assert correct user is passed to service hook function
        self.assertFalse(deactivate_services.called)

    @mock.patch('services.tasks.notify')
    @mock.patch('services.tasks.get_hooks')
    def test_deactivate_services(self, get_hooks, notify):
        """
        Test that hooks delete_user function is called by deactivate_services
        """
        svc = mock.Mock()
        svc.delete_user.return_value = True

        get_hooks.return_value = [lambda: svc]

        deactivate_services(self.member)

        self.assertTrue(get_hooks.called)
        args, kwargs = get_hooks.call_args
        self.assertEqual('services_hook', args[0])
        self.assertTrue(svc.delete_user.called)
        args, kwargs = svc.delete_user.call_args
        self.assertEqual(self.member, args[0])  # Assert correct user is passed to service hook function
        self.assertTrue(notify.called)
        args, kwargs = notify.call_args
        self.assertEqual(self.member, args[0])  # Assert user is passed to the notification system
        self.assertEqual("Services Disabled", args[1])
        self.assertEqual("danger", kwargs['level'])
