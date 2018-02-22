from unittest import mock

from django.test import TestCase

from allianceauth.tests.auth_utils import AuthUtils

from allianceauth.services.tasks import validate_services


class ServicesTasksTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_user('auth_member')

    @mock.patch('allianceauth.services.tasks.ServicesHook')
    def test_validate_services(self, services_hook):
        svc = mock.Mock()
        svc.validate_user.return_value = None

        services_hook.get_services.return_value = [svc]

        validate_services.delay(self.member.pk)

        self.assertTrue(services_hook.get_services.called)
        self.assertTrue(svc.validate_user.called)
        args, kwargs = svc.validate_user.call_args
        self.assertEqual(self.member, args[0])  # Assert correct user is passed to service hook function
