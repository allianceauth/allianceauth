from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from alliance_auth.tests.auth_utils import AuthUtils

from .auth_hooks import DiscordService
from .models import DiscordUser
from .tasks import DiscordTasks

MODULE_PATH = 'services.modules.discord'


def add_permissions():
    permission = Permission.objects.get(codename='access_discord')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class DiscordHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        DiscordUser.objects.create(user=member, uid='12345')
        self.blue = 'blue_user'
        blue = AuthUtils.create_blue(self.blue)
        DiscordUser.objects.create(user=blue, uid='67891')
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = DiscordService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(DiscordTasks.has_account(member))
        self.assertTrue(DiscordTasks.has_account(blue))
        self.assertFalse(DiscordTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 2)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(manager.update_groups.called)
            args, kwargs = manager.update_groups.call_args
            user_id, groups = args
            self.assertIn(settings.DEFAULT_AUTH_GROUP, groups)
            self.assertEqual(user_id, member.discord.uid)

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.update_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.discord)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        DiscordUser.objects.create(user=none_user, uid='abc123')
        service.validate_user(none_user)
        self.assertTrue(manager.delete_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_discord = User.objects.get(username=self.none_user).discord

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_sync_nickname(self, manager):
        service = self.service()
        member = User.objects.get(username=self.member)
        AuthUtils.add_main_character(member, 'test user', '12345', corp_ticker='AAUTH')

        service.sync_nickname(member)

        self.assertTrue(manager.update_nickname.called)
        args, kwargs = manager.update_nickname.call_args
        self.assertEqual(args[0], member.discord.uid)
        self.assertEqual(args[1], 'test user')

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.delete_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            discord_user = User.objects.get(username=self.member).discord

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn('/discord/reset/', response)
        self.assertIn('/discord/deactivate/', response)

        # Test register becomes available
        member.discord.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn('/discord/activate/', response)

    # TODO: Test update nicknames


class DiscordViewsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.member.set_password('password')
        self.member.save()
        add_permissions()

    def login(self):
        self.client.login(username=self.member.username, password='password')

    @mock.patch(MODULE_PATH + '.views.DiscordOAuthManager')
    def test_activate(self, manager):
        self.login()
        manager.generate_oauth_redirect_url.return_value = '/example.com/oauth/'
        response = self.client.get('/discord/activate/', follow=False)
        self.assertRedirects(response, expected_url='/example.com/oauth/', target_status_code=404)

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_callback(self, manager):
        self.login()
        manager.add_user.return_value = '1234'
        response = self.client.get('/discord/callback/', data={'code': '1234'})

        self.assertTrue(manager.add_user.called)
        self.assertEqual(manager.update_nickname.called, settings.DISCORD_SYNC_NAMES)
        self.assertEqual(self.member.discord.uid, '1234')
        self.assertRedirects(response, expected_url='/en/services/', target_status_code=200)

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_reset(self, manager):
        self.login()
        DiscordUser.objects.create(user=self.member, uid='12345')
        manager.delete_user.return_value = True

        response = self.client.get('/discord/reset/')

        self.assertRedirects(response, expected_url='/discord/activate/', target_status_code=302)

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_deactivate(self, manager):
        self.login()
        DiscordUser.objects.create(user=self.member, uid='12345')
        manager.delete_user.return_value = True

        response = self.client.get('/discord/deactivate/')

        self.assertTrue(manager.delete_user.called)
        self.assertRedirects(response, expected_url='/en/services/', target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            discord_user = User.objects.get(pk=self.member.pk).discord
