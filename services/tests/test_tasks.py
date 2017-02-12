from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase

from alliance_auth.tests.auth_utils import AuthUtils

from services.tasks import validate_services


class ServicesTasksTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.none_user = AuthUtils.create_user('none_user', disconnect_signals=True)

    @mock.patch('services.tasks.ServicesHook')
    def test_validate_services(self, services_hook):
        svc = mock.Mock()
        svc.validate_user.return_value = None

        services_hook.get_services.return_value = [svc]

        validate_services.delay(user=self.member)

        self.assertTrue(services_hook.get_services.called)
        self.assertTrue(svc.validate_user.called)
        args, kwargs = svc.validate_user.call_args
        self.assertEqual(self.member, args[0])  # Assert correct user is passed to service hook function
