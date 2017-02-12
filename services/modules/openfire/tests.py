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

from .auth_hooks import OpenfireService
from .models import OpenfireUser
from .tasks import OpenfireTasks

MODULE_PATH = 'services.modules.openfire'


def add_permissions():
    permission = Permission.objects.get(codename='access_openfire')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class OpenfireHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        OpenfireUser.objects.create(user=member, username=self.member)
        self.blue = 'blue_user'
        blue = AuthUtils.create_blue(self.blue)
        OpenfireUser.objects.create(user=blue, username=self.blue)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = OpenfireService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(OpenfireTasks.has_account(member))
        self.assertTrue(OpenfireTasks.has_account(blue))
        self.assertFalse(OpenfireTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_user_groups.called)
        self.assertEqual(manager.update_user_groups.call_count, 2)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.OpenfireManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_user_groups.called)
            args, kwargs = manager.update_user_groups.call_args
            user_id, groups = args
            self.assertIn(settings.DEFAULT_AUTH_GROUP, groups)
            self.assertEqual(user_id, member.openfire.username)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.OpenfireManager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_user_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.openfire)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        OpenfireUser.objects.create(user=none_user, username='abc123')
        service.validate_user(none_user)
        self.assertTrue(manager.delete_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_openfire = User.objects.get(username=self.none_user).openfire

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.delete_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            openfire_user = User.objects.get(username=self.member).openfire

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('auth_deactivate_openfire'), response)
        self.assertIn(urls.reverse('auth_reset_openfire_password'), response)
        self.assertIn(urls.reverse('auth_set_openfire_password'), response)

        # Test register becomes available
        member.openfire.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('auth_activate_openfire'), response)


class OpenfireViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.set_password('password')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.login(username=self.member.username, password='password')

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    @mock.patch(MODULE_PATH + '.views.OpenfireManager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('auth_activate_openfire'))

        self.assertTrue(manager.add_user.called)
        self.assertTrue(tasks_manager.update_user_groups.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registered/service_credentials.html')
        self.assertContains(response, expected_username)
        openfire_user = OpenfireUser.objects.get(user=self.member)
        self.assertEqual(openfire_user.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    def test_deactivate(self, manager):
        self.login()
        OpenfireUser.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('auth_deactivate_openfire'))

        self.assertTrue(manager.delete_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            openfire_user = User.objects.get(pk=self.member.pk).openfire

    @mock.patch(MODULE_PATH + '.views.OpenfireManager')
    def test_set_password(self, manager):
        self.login()
        OpenfireUser.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('auth_set_openfire_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_pass.called)
        args, kwargs = manager.update_user_pass.call_args
        self.assertEqual(kwargs['password'], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.OpenfireManager')
    def test_reset_password(self, manager):
        self.login()
        OpenfireUser.objects.create(user=self.member, username='some member')

        manager.update_user_pass.return_value = 'hunter2'

        response = self.client.get(urls.reverse('auth_reset_openfire_password'))

        self.assertTemplateUsed(response, 'registered/service_credentials.html')
        self.assertContains(response, 'some member')
        self.assertContains(response, 'hunter2')


class OpenfireManagerTestCase(TestCase):
    def setUp(self):
        from .manager import OpenfireManager
        self.manager = OpenfireManager

    def test_generate_random_password(self):
        password = self.manager._OpenfireManager__generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))

    def test__sanitize_username(self):
        test_username = " My_Test User\"'&/:<>@name\\20name"

        result_username = self.manager._OpenfireManager__sanitize_username(test_username)

        self.assertEqual(result_username, 'My_Test\\20User\\22\\27\\26\\2f\\3a\\3c\\3e\\40name\\5c20name')
