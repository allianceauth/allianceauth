from unittest import mock

from django.test import TestCase, RequestFactory
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import Ips4Service
from .models import Ips4User
from .tasks import Ips4Tasks

MODULE_PATH = 'allianceauth.services.modules.ips4'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_ips4')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class Ips4HooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        Ips4User.objects.create(user=member, id='12345', username=self.member)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = Ips4Service
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(Ips4Tasks.has_account(member))
        self.assertFalse(Ips4Tasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('ips4:set_password'), response)
        self.assertIn(urls.reverse('ips4:reset_password'), response)
        self.assertIn(urls.reverse('ips4:deactivate'), response)

        # Test register becomes available
        member.ips4.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('ips4:activate'), response)


class Ips4ViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.force_login(self.member)

    @mock.patch(MODULE_PATH + '.views.Ips4Manager')
    def test_activate(self, manager):
        self.login()
        expected_username = 'auth_member'
        expected_password = 'password'
        expected_id = '1234'

        manager.add_user.return_value = (expected_username, expected_password, expected_id)

        response = self.client.get(urls.reverse('ips4:activate'), follow=False)

        self.assertTrue(manager.add_user.called)
        args, kwargs = manager.add_user.call_args
        self.assertEqual(args[0], expected_username)
        self.assertEqual(args[1], self.member.email)

        self.assertTemplateUsed(response, 'services/service_credentials.html')
        self.assertContains(response, expected_username)
        self.assertContains(response, expected_password)

    @mock.patch(MODULE_PATH + '.tasks.Ips4Manager')
    def test_deactivate(self, manager):
        self.login()
        Ips4User.objects.create(user=self.member, username='12345', id='1234')
        manager.delete_user.return_value = True

        response = self.client.get(urls.reverse('ips4:deactivate'))

        self.assertTrue(manager.delete_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            ips4_user = User.objects.get(pk=self.member.pk).ips4

    @mock.patch(MODULE_PATH + '.views.Ips4Manager')
    def test_set_password(self, manager):
        self.login()
        Ips4User.objects.create(user=self.member, username='12345', id='1234')
        expected_password = 'password'
        manager.update_user_password.return_value = expected_password

        response = self.client.post(urls.reverse('ips4:set_password'), data={'password': expected_password})

        self.assertTrue(manager.update_custom_password.called)
        args, kwargs = manager.update_custom_password.call_args
        self.assertEqual(kwargs['plain_password'], expected_password)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.Ips4Manager')
    def test_reset_password(self, manager):
        self.login()
        Ips4User.objects.create(user=self.member, username='12345', id='1234')

        response = self.client.get(urls.reverse('ips4:reset_password'))

        self.assertTrue(manager.update_user_password.called)
        self.assertTemplateUsed(response, 'services/service_credentials.html')


class Ips4ManagerTestCase(TestCase):
    def setUp(self):
        from .manager import Ips4Manager
        self.manager = Ips4Manager

    def test_generate_random_password(self):
        password = self.manager._Ips4Manager__generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))

    def test_gen_pwhash(self):
        pwhash = self.manager._gen_pwhash('test')
        salt = self.manager._get_salt(pwhash)

        self.assertIsInstance(pwhash, str)
        self.assertGreaterEqual(len(pwhash), 59)
        self.assertIsInstance(salt, str)
        self.assertEqual(len(salt), 22)
