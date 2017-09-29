from unittest import mock

from django.test import TestCase, RequestFactory
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import SmfService
from .models import SmfUser
from .tasks import SmfTasks

MODULE_PATH = 'allianceauth.services.modules.smf'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_smf')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class SmfHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        SmfUser.objects.create(user=member, username=self.member)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = SmfService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(SmfTasks.has_account(member))
        self.assertFalse(SmfTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.SmfManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 1)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.SmfManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_groups.called)
            args, kwargs = manager.update_groups.call_args
            user_id, groups = args
            self.assertIn(DEFAULT_AUTH_GROUP, groups)
            self.assertEqual(user_id, member.smf.username)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.SmfManager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.SmfManager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.smf)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        SmfUser.objects.create(user=none_user, username='abc123')
        service.validate_user(none_user)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_smf = User.objects.get(username=self.none_user).smf

    @mock.patch(MODULE_PATH + '.tasks.SmfManager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            smf_user = User.objects.get(username=self.member).smf

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('smf:deactivate'), response)
        self.assertIn(urls.reverse('smf:reset_password'), response)
        self.assertIn(urls.reverse('smf:set_password'), response)

        # Test register becomes available
        member.smf.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('smf:activate'), response)


class SmfViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.force_login(self.member)

    @mock.patch(MODULE_PATH + '.tasks.SmfManager')
    @mock.patch(MODULE_PATH + '.views.SmfManager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('smf:activate'))

        self.assertTrue(manager.add_user.called)
        self.assertTrue(tasks_manager.update_groups.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('services/service_credentials.html')
        self.assertContains(response, expected_username)
        smf_user = SmfUser.objects.get(user=self.member)
        self.assertEqual(smf_user.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.SmfManager')
    def test_deactivate(self, manager):
        self.login()
        SmfUser.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('smf:deactivate'))

        self.assertTrue(manager.disable_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            smf_user = User.objects.get(pk=self.member.pk).smf

    @mock.patch(MODULE_PATH + '.views.SmfManager')
    def test_set_password(self, manager):
        self.login()
        SmfUser.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('smf:set_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_password.called)
        args, kwargs = manager.update_user_password.call_args
        self.assertEqual(kwargs['password'], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.SmfManager')
    def test_reset_password(self, manager):
        self.login()
        SmfUser.objects.create(user=self.member, username='some member')

        manager.update_user_password.return_value = 'hunter2'

        response = self.client.get(urls.reverse('smf:reset_password'))

        self.assertTemplateUsed(response, 'services/service_credentials.html')
        self.assertContains(response, 'some member')
        self.assertContains(response, 'hunter2')


class SmfManagerTestCase(TestCase):
    def setUp(self):
        from .manager import SmfManager
        self.manager = SmfManager

    def test_generate_random_password(self):
        password = self.manager.generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))

    def test_gen_hash(self):
        pwhash = self.manager.gen_hash('username', 'test')

        self.assertEqual(pwhash, 'b6d21d37de84db76746b1c45696a00f9ce4f86fd')
