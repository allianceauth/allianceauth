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

from .auth_hooks import SeatService
from .models import SeatUser
from .tasks import SeatTasks

MODULE_PATH = 'services.modules.seat'


def add_permissions():
    permission = Permission.objects.get(codename='access_seat')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class SeatHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        SeatUser.objects.create(user=member, username=self.member)
        self.blue = 'blue_user'
        blue = AuthUtils.create_blue(self.blue)
        SeatUser.objects.create(user=blue, username=self.blue)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user, disconnect_signals=True)
        self.service = SeatService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(SeatTasks.has_account(member))
        self.assertTrue(SeatTasks.has_account(blue))
        self.assertFalse(SeatTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_roles.called)
        self.assertEqual(manager.update_roles.call_count, 2)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.SeatManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_roles.called)
            args, kwargs = manager.update_roles.call_args
            user_id, groups = args
            self.assertIn(settings.DEFAULT_AUTH_GROUP, groups)
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
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('auth_deactivate_seat'), response)
        self.assertIn(urls.reverse('auth_reset_seat_password'), response)
        self.assertIn(urls.reverse('auth_set_seat_password'), response)

        # Test register becomes available
        member.seat.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('auth_activate_seat'), response)


class SeatViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.set_password('password')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    def login(self):
        self.client.login(username=self.member.username, password='password')

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    @mock.patch(MODULE_PATH + '.views.SeatManager')
    def test_activate(self, manager, tasks_manager):
        self.login()
        expected_username = 'auth_member'
        manager.check_user_status.return_value = {}
        manager.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('auth_activate_seat'))

        self.assertTrue(manager.add_user.called)
        self.assertTrue(tasks_manager.update_roles.called)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registered/service_credentials.html')
        self.assertContains(response, expected_username)
        seat_user = SeatUser.objects.get(user=self.member)
        self.assertEqual(seat_user.username, expected_username)
        self.assertTrue(manager.synchronize_eveapis.called)

    @mock.patch(MODULE_PATH + '.tasks.SeatManager')
    def test_deactivate(self, manager):
        self.login()
        SeatUser.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('auth_deactivate_seat'))

        self.assertTrue(manager.disable_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            seat_user = User.objects.get(pk=self.member.pk).seat

    @mock.patch(MODULE_PATH + '.views.SeatManager')
    def test_set_password(self, manager):
        self.login()
        SeatUser.objects.create(user=self.member, username='some member')

        response = self.client.post(urls.reverse('auth_set_seat_password'), data={'password': '1234asdf'})

        self.assertTrue(manager.update_user_password.called)
        args, kwargs = manager.update_user_password.call_args
        self.assertEqual(kwargs['plain_password'], '1234asdf')
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.views.SeatManager')
    def test_reset_password(self, manager):
        self.login()
        SeatUser.objects.create(user=self.member, username='some member')

        manager.update_user_password.return_value = 'hunter2'

        response = self.client.get(urls.reverse('auth_reset_seat_password'))

        self.assertTemplateUsed(response, 'registered/service_credentials.html')
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
