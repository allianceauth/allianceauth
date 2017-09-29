from unittest import mock

from django.test import TestCase, RequestFactory
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import OpenfireService
from .models import OpenfireUser
from .tasks import OpenfireTasks

MODULE_PATH = 'allianceauth.services.modules.openfire'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_openfire')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class OpenfireHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        OpenfireUser.objects.create(user=member, username=self.member)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = OpenfireService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(OpenfireTasks.has_account(member))
        self.assertFalse(OpenfireTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_user_groups.called)
        self.assertEqual(manager.update_user_groups.call_count, 1)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.OpenfireManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_user_groups.called)
            args, kwargs = manager.update_user_groups.call_args
            user_id, groups = args
            self.assertIn(DEFAULT_AUTH_GROUP, groups)
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
        request = RequestFactory().get('/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('openfire:deactivate'), response)
        self.assertIn(urls.reverse('openfire:reset_password'), response)
        self.assertIn(urls.reverse('openfire:set_password'), response)

        # Test register becomes available
        member.openfire.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('openfire:activate'), response)


class OpenfireViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.force_login(self.member)

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    @mock.patch(MODULE_PATH + '.views.OpenfireManager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('openfire:activate'))

        self.assertTrue(manager.add_user.called)
        self.assertTrue(tasks_manager.update_user_groups.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('services/service_credentials.html')
        self.assertContains(response, expected_username)
        openfire_user = OpenfireUser.objects.get(user=self.member)
        self.assertEqual(openfire_user.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.OpenfireManager')
    def test_deactivate(self, manager):
        self.login()
        OpenfireUser.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('openfire:deactivate'))

        self.assertTrue(manager.delete_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            openfire_user = User.objects.get(pk=self.member.pk).openfire

    @mock.patch(MODULE_PATH + '.views.OpenfireManager')
    def test_set_password(self, manager):
        self.login()
        OpenfireUser.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('openfire:set_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_pass.called)
        args, kwargs = manager.update_user_pass.call_args
        self.assertEqual(kwargs['password'], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.OpenfireManager')
    def test_reset_password(self, manager):
        self.login()
        OpenfireUser.objects.create(user=self.member, username='some member')

        manager.update_user_pass.return_value = 'hunter2'

        response = self.client.get(urls.reverse('openfire:reset_password'))

        self.assertTemplateUsed(response, 'services/service_credentials.html')
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

    def test__sanitize_groupname(self):
        test_groupname = " My_Test Groupname"

        result_groupname = self.manager._sanitize_groupname(test_groupname)

        self.assertEqual(result_groupname, "my_testgroupname")

    @mock.patch(MODULE_PATH + '.manager.ofUsers')
    def test_update_user_groups(self, api):
        groups = ["AddGroup", "othergroup", "Guest Group"]
        server_groups = ["othergroup", "Guest Group", "REMOVE group"]
        username = "testuser"
        api_instance = api.return_value
        api_instance.get_user_groups.return_value = {'groupname': server_groups}

        self.manager.update_user_groups(username, groups)

        self.assertTrue(api_instance.add_user_groups.called)
        args, kwargs = api_instance.add_user_groups.call_args
        self.assertEqual(args[1], ["addgroup"])

        self.assertTrue(api_instance.delete_user_groups.called)
        args, kwargs = api_instance.delete_user_groups.call_args
        self.assertEqual(args[1], ["removegroup"])
