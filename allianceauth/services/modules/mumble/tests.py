from unittest import mock

from django.test import TestCase, RequestFactory
from django import urls
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import MumbleService
from .models import MumbleUser
from .tasks import MumbleTasks

MODULE_PATH = 'allianceauth.services.modules.mumble'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_mumble')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class MumbleHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        MumbleUser.objects.create(user=member)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = MumbleService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(MumbleTasks.has_account(member))
        self.assertFalse(MumbleTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.User.mumble')
    def test_update_all_groups(self, mumble):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(mumble.update_groups.called)
        self.assertEqual(mumble.update_groups.call_count, 1)

    def test_update_groups(self):
        # Check member has Member group updated
        service = self.service()
        member = User.objects.get(username=self.member)
        member.mumble.groups = ''  # Remove the group set in setUp
        member.mumble.save()

        service.update_groups(member)

        mumble_user = MumbleUser.objects.get(user=member)
        self.assertIn(DEFAULT_AUTH_GROUP, mumble_user.groups)

        # Check none user does not have groups updated
        service = self.service()
        none_user = User.objects.get(username=self.none_user)
        result = service.update_groups(none_user)
        self.assertFalse(result)

    def test_validate_user(self):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.mumble)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        MumbleUser.objects.create(user=none_user)
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
        request = RequestFactory().get('/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('mumble:deactivate'), response)
        self.assertIn(urls.reverse('mumble:reset_password'), response)
        self.assertIn(urls.reverse('mumble:set_password'), response)

        # Test register becomes available
        member.mumble.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('mumble:activate'), response)


class MumbleViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation',
                                     corp_ticker='TESTR')
        add_permissions()

    def login(self):
        self.client.force_login(self.member)

    def test_activate(self):
        self.login()
        expected_username = '[TESTR]auth_member'
        response = self.client.get(urls.reverse('mumble:activate'), follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_username)
        mumble_user = MumbleUser.objects.get(user=self.member)
        self.assertEqual(mumble_user.username, expected_username)
        self.assertTrue(mumble_user.pwhash)
        self.assertIn('Guest', mumble_user.groups)
        self.assertIn('Member', mumble_user.groups)
        self.assertIn(',', mumble_user.groups)

    def test_deactivate_post(self):
        self.login()
        MumbleUser.objects.create(user=self.member)

        response = self.client.post(urls.reverse('mumble:deactivate'))

        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            mumble_user = User.objects.get(pk=self.member.pk).mumble

    def test_set_password(self):
        self.login()
        created = MumbleUser.objects.create(user=self.member)
        old_pwd = created.credentials.get('password')

        response = self.client.post(urls.reverse('mumble:set_password'), data={'password': '1234asdf'})

        self.assertNotEqual(MumbleUser.objects.get(user=self.member).pwhash, old_pwd)
        self.assertRedirects(response, expected_url=urls.reverse('services:services'), target_status_code=200)

    def test_reset_password(self):
        self.login()
        created = MumbleUser.objects.create(user=self.member)
        old_pwd = created.credentials.get('password')

        response = self.client.get(urls.reverse('mumble:reset_password'))

        self.assertNotEqual(MumbleUser.objects.get(user=self.member).pwhash, old_pwd)
        self.assertTemplateUsed(response, 'services/service_credentials.html')
        self.assertContains(response, 'auth_member')


class MumbleManagerTestCase(TestCase):
    def setUp(self):
        from .models import MumbleManager
        self.manager = MumbleManager

    def test_generate_random_password(self):
        password = self.manager.generate_random_pass()

        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, type(''))

    def test_gen_pwhash(self):
        pwhash = self.manager.gen_pwhash('test')

        self.assertEqual(pwhash[:15], '$bcrypt-sha256$')
        self.assertEqual(len(pwhash), 75)
