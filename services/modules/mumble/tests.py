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

from .auth_hooks import MumbleService
from .models import MumbleUser
from .tasks import MumbleTasks

MODULE_PATH = 'services.modules.mumble'


def add_permissions():
    permission = Permission.objects.get(codename='access_mumble')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class MumbleHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        MumbleUser.objects.create(user=member, username=self.member, pwhash='password', groups='Member')
        self.blue = 'blue_user'
        blue = AuthUtils.create_blue(self.blue)
        MumbleUser.objects.create(user=blue, username=self.blue, pwhash='password', groups='Blue')
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = MumbleService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(MumbleTasks.has_account(member))
        self.assertTrue(MumbleTasks.has_account(blue))
        self.assertFalse(MumbleTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.MumbleManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 2)

    def test_update_groups(self):
        # Check member has Member group updated
        service = self.service()
        member = User.objects.get(username=self.member)
        member.mumble.groups = ''  # Remove the group set in setUp
        member.mumble.save()

        service.update_groups(member)

        mumble_user = MumbleUser.objects.get(user=member)
        self.assertIn(settings.DEFAULT_AUTH_GROUP, mumble_user.groups)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.MumbleManager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_groups.called)

    def test_validate_user(self):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.mumble)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        MumbleUser.objects.create(user=none_user, username='mr no-name', pwhash='password', groups='Blue,Orange')
        service.validate_user(none_user)
        with self.assertRaises(ObjectDoesNotExist):
            none_mumble = User.objects.get(username=self.none_user).mumble

    def test_delete_user(self):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        with self.assertRaises(ObjectDoesNotExist):
            mumble_user = User.objects.get(username=self.member).mumble

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('auth_deactivate_mumble'), response)
        self.assertIn(urls.reverse('auth_reset_mumble_password'), response)
        self.assertIn(urls.reverse('auth_set_mumble_password'), response)

        # Test register becomes available
        member.mumble.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('auth_activate_mumble'), response)


class MumbleViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.set_password('password')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation',
                                     corp_ticker='TESTR')
        add_permissions()

    def login(self):
        self.client.login(username=self.member.username, password='password')

    def test_activate(self):
        self.login()
        expected_username = '[TESTR]auth_member'
        response = self.client.get(urls.reverse('auth_activate_mumble'), follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_username)
        mumble_user = MumbleUser.objects.get(user=self.member)
        self.assertEqual(mumble_user.username, expected_username)
        self.assertTrue(mumble_user.pwhash)
        self.assertEqual(self.member.mumble.username, expected_username)
        self.assertEqual('Member', mumble_user.groups)

    def test_deactivate(self):
        self.login()
        MumbleUser.objects.create(user=self.member, username='some member')

        response = self.client.get(urls.reverse('auth_deactivate_mumble'))

        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            mumble_user = User.objects.get(pk=self.member.pk).mumble

    def test_set_password(self):
        self.login()
        MumbleUser.objects.create(user=self.member, username='some member', pwhash='old')

        response = self.client.post(urls.reverse('auth_set_mumble_password'), data={'password': '1234asdf'})

        self.assertNotEqual(MumbleUser.objects.get(user=self.member).pwhash, 'old')
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)

    def test_reset_password(self):
        self.login()
        MumbleUser.objects.create(user=self.member, username='some member', pwhash='old')

        response = self.client.get(urls.reverse('auth_reset_mumble_password'))

        self.assertNotEqual(MumbleUser.objects.get(user=self.member).pwhash, 'old')
        self.assertTemplateUsed(response, 'registered/service_credentials.html')
        self.assertContains(response, 'some member')


class MumbleManagerTestCase(TestCase):
    def setUp(self):
        from .manager import MumbleManager
        self.manager = MumbleManager

    def test_generate_random_password(self):
        password = self.manager._MumbleManager__generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))

    def test_gen_pwhash(self):
        pwhash = self.manager._gen_pwhash('test')

        self.assertEqual(pwhash[:15], '$bcrypt-sha256$')
        self.assertEqual(len(pwhash), 75)
