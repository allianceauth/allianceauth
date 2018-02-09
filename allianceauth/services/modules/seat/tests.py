from unittest import mock

from django.test import TestCase, RequestFactory
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import SeatService
from .models import SeatUser
from .tasks import SeatTasks

MODULE_PATH = 'allianceauth.services.modules.seat'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_seat')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class SeatHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        SeatUser.objects.create(user=member, username=self.member)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user, disconnect_signals=True)
        self.service = SeatService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(SeatTasks.has_account(member))
        self.assertFalse(SeatTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_roles.called)
        self.assertEqual(manager.update_roles.call_count, 1)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.SeatManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_roles.called)
            args, kwargs = manager.update_roles.call_args
            user_id, groups = args
            self.assertIn(DEFAULT_AUTH_GROUP, groups)
            self.assertEqual(user_id, member.seat.username)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.SeatManager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_roles.called)

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        # Pre assertion
        self.assertTrue(member.has_perm('seat.access_seat'))

        service.validate_user(member)
        self.assertTrue(User.objects.get(username=self.member).seat)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        manager.disable_user.return_value = 'abc123'
        SeatUser.objects.create(user=none_user, username='abc123')
        service.validate_user(none_user)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_seat = User.objects.get(username=self.none_user).seat

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            seat_user = User.objects.get(username=self.member).seat

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('seat:deactivate'), response)
        self.assertIn(urls.reverse('seat:reset_password'), response)
        self.assertIn(urls.reverse('seat:set_password'), response)

        # Test register becomes available
        member.seat.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('seat:activate'), response)


class SeatViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.force_login(self.member)

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    @mock.patch(MODULE_PATH + '.views.SeatManager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.check_user_status.return_value = {}
        manager.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('seat:activate'))

        self.assertTrue(manager.add_user.called)
        self.assertTrue(tasks_manager.update_roles.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('services/service_credentials.html')
        self.assertContains(response, expected_username)
        seat_user = SeatUser.objects.get(user=self.member)
        self.assertEqual(seat_user.username, expected_username)

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    def test_deactivate(self, manager):
        self.login()
        SeatUser.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('seat:deactivate'))

        self.assertTrue(manager.disable_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

        with self.assertRaises(ObjectDoesNotExist):
            seat_user = User.objects.get(pk=self.member.pk).seat

    @mock.patch(MODULE_PATH + '.views.SeatManager')
    def test_set_password(self, manager):
        self.login()
        SeatUser.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('seat:set_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_password.called)
        args, kwargs = manager.update_user_password.call_args
        self.assertEqual(kwargs['plain_password'], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.SeatManager')
    def test_reset_password(self, manager):
        self.login()
        SeatUser.objects.create(user=self.member, username='some member')

        manager.update_user_password.return_value = 'hunter2'

        response = self.client.get(urls.reverse('seat:reset_password'))

        self.assertTemplateUsed(response, 'services/service_credentials.html')
        self.assertContains(response, 'some member')
        self.assertContains(response, 'hunter2')


class SeatManagerTestCase(TestCase):
    def setUp(self):
        from .manager import SeatManager
        self.manager = SeatManager

    def test_generate_random_password(self):
        password = self.manager._SeatManager__generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))
