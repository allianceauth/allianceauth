from unittest import mock

from django.test import TestCase, RequestFactory
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import Phpbb3Service
from .models import Phpbb3User
from .tasks import Phpbb3Tasks

MODULE_PATH = 'allianceauth.services.modules.phpbb3'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_phpbb3')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class Phpbb3HooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        Phpbb3User.objects.create(user=member, username=self.member)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = Phpbb3Service
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(Phpbb3Tasks.has_account(member))
        self.assertFalse(Phpbb3Tasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 1)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_groups.called)
            args, kwargs = manager.update_groups.call_args
            user_id, groups = args
            self.assertIn(DEFAULT_AUTH_GROUP, groups)
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
        request = RequestFactory().get('/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('phpbb3:deactivate'), response)
        self.assertIn(urls.reverse('phpbb3:reset_password'), response)
        self.assertIn(urls.reverse('phpbb3:set_password'), response)

        # Test register becomes available
        member.phpbb3.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('phpbb3:activate'), response)


class Phpbb3ViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.force_login(self.member)

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    @mock.patch(MODULE_PATH + '.views.Phpbb3Manager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('phpbb3:activate'))

        self.assertTrue(manager.add_user.called)
        self.assertTrue(tasks_manager.update_groups.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('services/service_credentials.html')
        self.assertContains(response, expected_username)
        phpbb3_user = Phpbb3User.objects.get(user=self.member)
        self.assertEqual(phpbb3_user.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.Phpbb3Manager')
    def test_deactivate(self, manager):
        self.login()
        Phpbb3User.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('phpbb3:deactivate'))

        self.assertTrue(manager.disable_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            phpbb3_user = User.objects.get(pk=self.member.pk).phpbb3

    @mock.patch(MODULE_PATH + '.views.Phpbb3Manager')
    def test_set_password(self, manager):
        self.login()
        Phpbb3User.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('phpbb3:set_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_password.called)
        args, kwargs = manager.update_user_password.call_args
        self.assertEqual(kwargs['password'], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.Phpbb3Manager')
    def test_reset_password(self, manager):
        self.login()
        Phpbb3User.objects.create(user=self.member, username='some member')

        manager.update_user_password.return_value = 'hunter2'

        response = self.client.get(urls.reverse('phpbb3:reset_password'))

        self.assertTemplateUsed(response, 'services/service_credentials.html')
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
