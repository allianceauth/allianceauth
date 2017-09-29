from unittest import mock

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import DiscourseService
from .models import DiscourseUser
from .tasks import DiscourseTasks

MODULE_PATH = 'allianceauth.services.modules.discourse'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_discourse')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class DiscourseHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        DiscourseUser.objects.create(user=member, enabled=True)
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = DiscourseService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(DiscourseTasks.has_account(member))
        self.assertFalse(DiscourseTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.DiscourseManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 1)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.DiscourseManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_groups.called)
            args, kwargs = manager.update_groups.call_args
            user, = args
            self.assertEqual(user, member)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.DiscourseManager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.DiscourseManager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.discourse)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        DiscourseUser.objects.create(user=none_user, enabled=True)
        service.validate_user(none_user)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_discourse = User.objects.get(username=self.none_user).discourse

    @mock.patch(MODULE_PATH + '.tasks.DiscourseManager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.disable_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            discourse_user = User.objects.get(username=self.member).discourse

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn('href="%s"' % settings.DISCOURSE_URL, response)


class DiscourseViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
        add_permissions()

    @mock.patch(MODULE_PATH + '.tasks.DiscourseManager')
    def test_sso_member(self, manager):
        self.client.force_login(self.member)
        data = {'sso': 'bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A',
                'sig': '2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56'}
        response = self.client.get('/discourse/sso', data=data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url[:37], 'https://example.com/session/sso_login')
