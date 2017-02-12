from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase, RequestFactory
from django.conf import settings
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from alliance_auth.tests.auth_utils import AuthUtils

from .auth_hooks import Ips4Service
from .models import Ips4User
from .tasks import Ips4Tasks

MODULE_PATH = 'services.modules.ips4'


def add_permissions():
    permission = Permission.objects.get(codename='access_ips4')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class Ips4HooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        Ips4User.objects.create(user=member, id='12345', username=self.member)
        self.blue = 'blue_user'
        blue = AuthUtils.create_blue(self.blue)
        Ips4User.objects.create(user=blue, id='67891', username=self.blue)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = Ips4Service
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(Ips4Tasks.has_account(member))
        self.assertTrue(Ips4Tasks.has_account(blue))
        self.assertFalse(Ips4Tasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('auth_set_ips4_password'), response)
        self.assertIn(urls.reverse('auth_reset_ips4_password'), response)
        self.assertIn(urls.reverse('auth_deactivate_ips4'), response)

        # Test register becomes available
        member.ips4.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('auth_activate_ips4'), response)


class Ips4ViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.set_password('password')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.login(username=self.member.username, password='password')

    @mock.patch(MODULE_PATH + '.views.Ips4Manager')
    def test_activate(self, manager):
        self.login()
        expected_username = 'auth_member'
        expected_password = 'password'
        expected_id = '1234'

        manager.add_user.return_value = (expected_username, expected_password, expected_id)

        response = self.client.get(urls.reverse('auth_activate_ips4'), follow=False)

        self.assertTrue(manager.add_user.called)
        args, kwargs = manager.add_user.call_args
        self.assertEqual(args[0], expected_username)
        self.assertEqual(args[1], self.member.email)

        self.assertTemplateUsed(response, 'registered/service_credentials.html')
        self.assertContains(response, expected_username)
        self.assertContains(response, expected_password)

    @mock.patch(MODULE_PATH + '.tasks.Ips4Manager')
    def test_deactivate(self, manager):
        self.login()
        Ips4User.objects.create(user=self.member, username='12345', id='1234')
        manager.delete_user.return_value = True

        response = self.client.get(urls.reverse('auth_deactivate_ips4'))

        self.assertTrue(manager.delete_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            ips4_user = User.objects.get(pk=self.member.pk).ips4

    @mock.patch(MODULE_PATH + '.views.Ips4Manager')
    def test_set_password(self, manager):
        self.login()
        Ips4User.objects.create(user=self.member, username='12345', id='1234')
        expected_password = 'password'
        manager.update_user_password.return_value = expected_password

        response = self.client.post(urls.reverse('auth_set_ips4_password'), data={'password': expected_password})

        self.assertTrue(manager.update_custom_password.called)
        args, kwargs = manager.update_custom_password.call_args
        self.assertEqual(kwargs['plain_password'], expected_password)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.Ips4Manager')
    def test_reset_password(self, manager):
        self.login()
        Ips4User.objects.create(user=self.member, username='12345', id='1234')

        response = self.client.get(urls.reverse('auth_reset_ips4_password'))

        self.assertTrue(manager.update_user_password.called)
        self.assertTemplateUsed(response, 'registered/service_credentials.html')


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
