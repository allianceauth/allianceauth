from unittest import mock

from django.test import TestCase, RequestFactory
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import XenforoService
from .models import XenforoUser
from .tasks import XenforoTasks

MODULE_PATH = 'allianceauth.services.modules.xenforo'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_xenforo')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class XenforoHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        XenforoUser.objects.create(user=member, username=self.member)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = XenforoService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(XenforoTasks.has_account(member))
        self.assertFalse(XenforoTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.XenForoManager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        manager.disable_user.return_value = 200

        service.validate_user(member)
        self.assertTrue(member.xenforo)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        XenforoUser.objects.create(user=none_user, username='abc123')
        service.validate_user(none_user)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_xenforo = User.objects.get(username=self.none_user).xenforo

    @mock.patch(MODULE_PATH + '.tasks.XenForoManager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)
        manager.disable_user.return_value = 200
        service = self.service()

        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            xenforo_user = User.objects.get(username=self.member).xenforo

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('xenforo:deactivate'), response)
        self.assertIn(urls.reverse('xenforo:reset_password'), response)
        self.assertIn(urls.reverse('xenforo:set_password'), response)

        # Test register becomes available
        member.xenforo.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('xenforo:activate'), response)


class XenforoViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.force_login(self.member)

    @mock.patch(MODULE_PATH + '.tasks.XenForoManager')
    @mock.patch(MODULE_PATH + '.views.XenForoManager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.add_user.return_value = {
            'response': {'status_code': 200},
            'password': 'hunter2',
            'username': expected_username,
        }

        response = self.client.get(urls.reverse('xenforo:activate'))

        self.assertTrue(manager.add_user.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('services/service_credentials.html')
        self.assertContains(response, expected_username)
        xenforo_user = XenforoUser.objects.get(user=self.member)
        self.assertEqual(xenforo_user.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.XenForoManager')
    def test_deactivate(self, manager):
        self.login()
        XenforoUser.objects.create(user=self.member, username='some member')

        manager.disable_user.return_value = 200

        response = self.client.get(urls.reverse('xenforo:deactivate'))

        self.assertTrue(manager.disable_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            xenforo_user = User.objects.get(pk=self.member.pk).xenforo

    @mock.patch(MODULE_PATH + '.views.XenForoManager')
    def test_set_password(self, manager):
        self.login()
        XenforoUser.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('xenforo:set_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_password.called)
        args, kwargs = manager.update_user_password.call_args
        self.assertEqual(args[1], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.XenForoManager')
    def test_reset_password(self, manager):
        self.login()
        XenforoUser.objects.create(user=self.member, username='some member')

        manager.reset_password.return_value = {
            'response': {'status_code': 200},
            'password': 'hunter2',
        }

        response = self.client.get(urls.reverse('xenforo:reset_password'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_credentials.html')
        self.assertContains(response, 'some member')
        self.assertContains(response, 'hunter2')


class XenforoManagerTestCase(TestCase):
    def setUp(self):
        from .manager import XenForoManager
        self.manager = XenForoManager

    def test_generate_password(self):
        password = self.manager._XenForoManager__generate_password()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))
