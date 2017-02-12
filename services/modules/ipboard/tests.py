from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django import urls
from django.core.exceptions import ObjectDoesNotExist

from alliance_auth.tests.auth_utils import AuthUtils

from .auth_hooks import IpboardService
from .models import IpboardUser
from .tasks import IpboardTasks
from .manager import IPBoardManager

MODULE_PATH = 'services.modules.ipboard'


def add_permissions():
    permission = Permission.objects.get(codename='access_ipboard')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class IpboardHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        IpboardUser.objects.create(user=member, username=self.member)
        self.blue = 'blue_user'
        blue = AuthUtils.create_blue(self.blue)
        IpboardUser.objects.create(user=blue, username=self.blue)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = IpboardService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(IpboardTasks.has_account(member))
        self.assertTrue(IpboardTasks.has_account(blue))
        self.assertFalse(IpboardTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.IPBoardManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 2)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.IPBoardManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_groups.called)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.IPBoardManager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.IPBoardManager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(User.objects.get(username=self.member).ipboard)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        IpboardUser.objects.create(user=none_user, username='none_user')
        service.validate_user(none_user)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_ipboard = User.objects.get(username=self.none_user).ipboard

    @mock.patch(MODULE_PATH + '.tasks.IPBoardManager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            Ipboard_user = User.objects.get(username=self.member).ipboard

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn('/ipboard/set_password/', response)
        self.assertIn('/ipboard/reset_password/', response)
        self.assertIn('/ipboard/deactivate/', response)

        # Test register becomes available
        member.ipboard.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn('/ipboard/activate/', response)


class IpboardViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.set_password('password')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.login(username=self.member.username, password='password')

    @mock.patch(MODULE_PATH + '.views.IPBoardManager')
    def test_activate(self, manager):
        self.login()
        expected_username = 'auth_member'
        expected_password = 'abc123'
        manager.add_user.return_value = (expected_username, expected_password)
        response = self.client.get(urls.reverse('auth_activate_ipboard'), follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_username)
        self.assertContains(response, expected_password)
        self.assertTrue(manager.add_user.called)
        args, kwargs = manager.add_user.call_args
        self.assertEqual(args[0], 'auth_member')  # Character name
        self.assertEqual(args[1], self.member.email)
        self.assertEqual(self.member.ipboard.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.IPBoardManager')
    def test_deactivate(self, manager):
        self.login()
        IpboardUser.objects.create(user=self.member, username='12345')
        manager.disable_user.return_value = True

        response = self.client.get(urls.reverse('auth_deactivate_ipboard'))

        self.assertTrue(manager.disable_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            ipboard_user = User.objects.get(pk=self.member.pk).ipboard

    @mock.patch(MODULE_PATH + '.views.IPBoardManager')
    def test_set_password(self, manager):
        self.login()
        IpboardUser.objects.create(user=self.member, username='12345')
        expected_password = 'password'
        manager.update_user_password.return_value = expected_password

        response = self.client.post(urls.reverse('auth_set_ipboard_password'), data={'password': expected_password})

        self.assertTrue(manager.update_user_password.called)
        args, kwargs = manager.update_user_password.call_args
        self.assertEqual(kwargs['plain_password'], expected_password)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.IPBoardManager')
    def test_reset_password(self, manager):
        self.login()
        IpboardUser.objects.create(user=self.member, username='12345')

        response = self.client.get(urls.reverse('auth_reset_ipboard_password'))

        self.assertTrue(manager.update_user_password.called)
        self.assertTemplateUsed(response, 'registered/service_credentials.html')


class IpboardManagerTestCase(TestCase):
    def setUp(self):
        self.manager = IPBoardManager

    def test_generate_random_password(self):
        password = self.manager._IPBoardManager__generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))

    def test_gen_pwhash(self):
        pwhash = self.manager._gen_pwhash('test')

        self.assertEqual(pwhash, '098f6bcd4621d373cade4e832627b4f6')
