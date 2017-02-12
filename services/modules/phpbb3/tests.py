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

from .auth_hooks import Phpbb3Service
from .models import Phpbb3User
from .tasks import Phpbb3Tasks

MODULE_PATH = 'services.modules.phpbb3'


def add_permissions():
    permission = Permission.objects.get(codename='access_phpbb3')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class Phpbb3HooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        Phpbb3User.objects.create(user=member, username=self.member)
        self.blue = 'blue_user'
        blue = AuthUtils.create_blue(self.blue)
        Phpbb3User.objects.create(user=blue, username=self.blue)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = Phpbb3Service
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(Phpbb3Tasks.has_account(member))
        self.assertTrue(Phpbb3Tasks.has_account(blue))
        self.assertFalse(Phpbb3Tasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 2)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_groups.called)
            args, kwargs = manager.update_groups.call_args
            user_id, groups = args
            self.assertIn(settings.DEFAULT_AUTH_GROUP, groups)
            self.assertEqual(user_id, member.phpbb3.username)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.phpbb3)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        Phpbb3User.objects.create(user=none_user, username='abc123')
        service.validate_user(none_user)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_phpbb3 = User.objects.get(username=self.none_user).phpbb3

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            phpbb3_user = User.objects.get(username=self.member).phpbb3

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('auth_deactivate_phpbb3'), response)
        self.assertIn(urls.reverse('auth_reset_phpbb3_password'), response)
        self.assertIn(urls.reverse('auth_set_phpbb3_password'), response)

        # Test register becomes available
        member.phpbb3.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('auth_activate_phpbb3'), response)


class Phpbb3ViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.set_password('password')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.login(username=self.member.username, password='password')

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    @mock.patch(MODULE_PATH + '.views.Phpbb3Manager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('auth_activate_phpbb3'))

        self.assertTrue(manager.add_user.called)
        self.assertTrue(tasks_manager.update_groups.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registered/service_credentials.html')
        self.assertContains(response, expected_username)
        phpbb3_user = Phpbb3User.objects.get(user=self.member)
        self.assertEqual(phpbb3_user.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    def test_deactivate(self, manager):
        self.login()
        Phpbb3User.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('auth_deactivate_phpbb3'))

        self.assertTrue(manager.disable_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            phpbb3_user = User.objects.get(pk=self.member.pk).phpbb3

    @mock.patch(MODULE_PATH + '.views.Phpbb3Manager')
    def test_set_password(self, manager):
        self.login()
        Phpbb3User.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('auth_set_phpbb3_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_password.called)
        args, kwargs = manager.update_user_password.call_args
        self.assertEqual(kwargs['password'], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.Phpbb3Manager')
    def test_reset_password(self, manager):
        self.login()
        Phpbb3User.objects.create(user=self.member, username='some member')

        manager.update_user_password.return_value = 'hunter2'

        response = self.client.get(urls.reverse('auth_reset_phpbb3_password'))

        self.assertTemplateUsed(response, 'registered/service_credentials.html')
        self.assertContains(response, 'some member')
        self.assertContains(response, 'hunter2')


class Phpbb3ManagerTestCase(TestCase):
    def setUp(self):
        from .manager import Phpbb3Manager
        self.manager = Phpbb3Manager

    def test_generate_random_password(self):
        password = self.manager._Phpbb3Manager__generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))

    def test_gen_pwhash(self):
        pwhash = self.manager._Phpbb3Manager__gen_hash('test')

        self.assertIsInstance(pwhash, str)
