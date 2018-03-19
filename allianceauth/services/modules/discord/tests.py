import json
import urllib
import datetime
import requests_mock
from django_webtest import WebTest
from unittest import mock

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import DiscordService
from .models import DiscordUser
from .tasks import DiscordTasks
from .manager import DiscordOAuthManager
from . import manager


MODULE_PATH = 'allianceauth.services.modules.discord'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_discord')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class DiscordHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        DiscordUser.objects.create(user=member, uid='12345')
        self.none_user = 'none_user'
        none_user = AuthUtils.create_user(self.none_user)
        self.service = DiscordService
        add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(DiscordTasks.has_account(member))
        self.assertFalse(DiscordTasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_update_all_groups(self, manager):
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(manager.update_groups.called)
        self.assertEqual(manager.update_groups.call_count, 1)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager') as manager:
            service = self.service()
            member = User.objects.get(username=self.member)
            AuthUtils.disconnect_signals()
            service.update_groups(member)
            self.assertTrue(manager.update_groups.called)
            args, kwargs = manager.update_groups.call_args
            user_id, groups = args
            self.assertIn(DEFAULT_AUTH_GROUP, groups)
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
        request = RequestFactory().get('/services/')
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


class DiscordViewsTestCase(WebTest):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        AuthUtils.add_main_character(self.member, 'test character', '1234', '2345', 'test corp', 'testc')
        add_permissions()

    def login(self):
        self.app.set_user(self.member)

    @mock.patch(MODULE_PATH + '.views.DiscordOAuthManager')
    def test_activate(self, manager):
        self.login()
        manager.generate_oauth_redirect_url.return_value = '/example.com/oauth/'
        response = self.app.get('/discord/activate/', auto_follow=False)
        self.assertRedirects(response, expected_url='/example.com/oauth/', target_status_code=404)

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_callback(self, manager):
        self.login()
        manager.add_user.return_value = '1234'
        response = self.app.get('/discord/callback/', params={'code': '1234'})

        self.member = User.objects.get(pk=self.member.pk)

        self.assertTrue(manager.add_user.called)
        self.assertEqual(manager.update_nickname.called, settings.DISCORD_SYNC_NAMES)
        self.assertEqual(self.member.discord.uid, '1234')
        self.assertRedirects(response, expected_url='/services/', target_status_code=200)

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_reset(self, manager):
        self.login()
        DiscordUser.objects.create(user=self.member, uid='12345')
        manager.delete_user.return_value = True

        response = self.app.get('/discord/reset/')

        self.assertRedirects(response, expected_url='/discord/activate/', target_status_code=302)

    @mock.patch(MODULE_PATH + '.tasks.DiscordOAuthManager')
    def test_deactivate(self, manager):
        self.login()
        DiscordUser.objects.create(user=self.member, uid='12345')
        manager.delete_user.return_value = True

        response = self.app.get('/discord/deactivate/')

        self.assertTrue(manager.delete_user.called)
        self.assertRedirects(response, expected_url='/services/', target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            discord_user = User.objects.get(pk=self.member.pk).discord


class DiscordManagerTestCase(TestCase):
    def setUp(self):
        pass

    def test__sanitize_group_name(self):
        test_group_name = str(10**103)
        group_name = DiscordOAuthManager._sanitize_group_name(test_group_name)

        self.assertEqual(group_name, test_group_name[:100])

    def test_generate_Bot_add_url(self):
        bot_add_url = DiscordOAuthManager.generate_bot_add_url()

        auth_url = manager.AUTH_URL
        real_bot_add_url = '{}?client_id=appid&scope=bot&permissions={}'.format(auth_url, manager.BOT_PERMISSIONS)
        self.assertEqual(bot_add_url, real_bot_add_url)

    def test_generate_oauth_redirect_url(self):
        oauth_url = DiscordOAuthManager.generate_oauth_redirect_url()

        self.assertIn(manager.AUTH_URL, oauth_url)
        self.assertIn('+'.join(manager.SCOPES), oauth_url)
        self.assertIn(settings.DISCORD_APP_ID, oauth_url)
        self.assertIn(urllib.parse.quote_plus(settings.DISCORD_CALLBACK_URL), oauth_url)

    @mock.patch(MODULE_PATH + '.manager.OAuth2Session')
    def test__process_callback_code(self, oauth):
        instance = oauth.return_value
        instance.fetch_token.return_value = {'access_token': 'mywonderfultoken'}

        token = DiscordOAuthManager._process_callback_code('12345')

        self.assertTrue(oauth.called)
        args, kwargs = oauth.call_args
        self.assertEqual(args[0], settings.DISCORD_APP_ID)
        self.assertEqual(kwargs['redirect_uri'], settings.DISCORD_CALLBACK_URL)
        self.assertTrue(instance.fetch_token.called)
        args, kwargs = instance.fetch_token.call_args
        self.assertEqual(args[0], manager.TOKEN_URL)
        self.assertEqual(kwargs['client_secret'], settings.DISCORD_APP_SECRET)
        self.assertEqual(kwargs['code'], '12345')
        self.assertEqual(token['access_token'], 'mywonderfultoken')

    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._process_callback_code')
    @requests_mock.Mocker()
    def test_add_user(self, oauth_token, m):
        # Arrange
        oauth_token.return_value = {'access_token': 'accesstoken'}

        headers = {'accept': 'application/json', 'authorization': 'Bearer accesstoken'}

        m.register_uri('GET',
                       manager.DISCORD_URL + "/users/@me",
                       request_headers=headers,
                       text=json.dumps({'id': "123456"}))

        headers = {'accept': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}

        m.register_uri('PUT',
                       manager.DISCORD_URL + '/guilds/' + str(settings.DISCORD_GUILD_ID) + '/members/123456',
                       request_headers=headers,
                       text='{}')

        # Act
        return_value = DiscordOAuthManager.add_user('abcdef', [])

        # Assert
        self.assertEqual(return_value, '123456')
        self.assertEqual(m.call_count, 2)

    @requests_mock.Mocker()
    def test_delete_user(self, m):
        # Arrange
        headers = {'accept': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}

        user_id = 12345
        request_url = '{}/guilds/{}/members/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id)
        m.register_uri('DELETE',
                       request_url,
                       request_headers=headers,
                       text=json.dumps({}))

        # Act
        result = DiscordOAuthManager.delete_user(user_id)

        # Assert
        self.assertTrue(result)

        ###
        # Test 404 (already deleted)
        # Arrange
        m.register_uri('DELETE',
                       request_url,
                       request_headers=headers,
                       status_code=404)

        # Act
        result = DiscordOAuthManager.delete_user(user_id)

        # Assert
        self.assertTrue(result)

        ###
        # Test 500 (some random API error)
        # Arrange
        m.register_uri('DELETE',
                       request_url,
                       request_headers=headers,
                       status_code=500)

        # Act
        result = DiscordOAuthManager.delete_user(user_id)

        # Assert
        self.assertFalse(result)

    @requests_mock.Mocker()
    def test_update_nickname(self, m):
        # Arrange
        headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}

        user_id = 12345
        request_url = '{}/guilds/{}/members/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id)
        m.patch(request_url,
                request_headers=headers)

        # Act
        result = DiscordOAuthManager.update_nickname(user_id, 'somenick')

        # Assert
        self.assertTrue(result)

    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._get_user_roles')
    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._get_groups')
    @requests_mock.Mocker()
    def test_update_groups(self, group_cache, user_roles, m):
        # Arrange
        groups = ['Member', 'Blue', 'SpecialGroup']

        group_cache.return_value = [{'id': '111', 'name': 'Member'},
                                    {'id': '222', 'name': 'Blue'},
                                    {'id': '333', 'name': 'SpecialGroup'},
                                    {'id': '444', 'name': 'NotYourGroup'}]
        user_roles.return_value = ['444']

        headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        user_id = 12345
        user_request_url = '{}/guilds/{}/members/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id)
        group_request_urls = ['{}/guilds/{}/members/{}/roles/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id, g['id']) for g in group_cache.return_value]

        m.patch(user_request_url, request_headers=headers)
        [m.put(url, request_headers=headers) for url in group_request_urls[:-1]]
        m.delete(group_request_urls[-1], request_headers=headers)

        # Act
        DiscordOAuthManager.update_groups(user_id, groups)

        # Assert
        self.assertEqual(len(m.request_history), 4, 'Must be 4 HTTP calls made')

    @mock.patch(MODULE_PATH + '.manager.cache')
    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._get_user_roles')
    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._group_name_to_id')
    @requests_mock.Mocker()
    def test_update_groups_backoff(self, name_to_id, user_groups, djcache, m):
        # Arrange
        groups = ['Member']
        user_groups.return_value = []
        name_to_id.return_value = '111'

        headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        user_id = 12345
        request_url = '{}/guilds/{}/members/{}/roles/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id, name_to_id.return_value)

        djcache.get.return_value = None  # No existing backoffs in cache

        m.put(request_url,
              request_headers=headers,
              headers={'Retry-After': '200000'},
              status_code=429)

        # Act & Assert
        with self.assertRaises(manager.DiscordApiBackoff) as bo:
            try:
                DiscordOAuthManager.update_groups(user_id, groups, blocking=False)
            except manager.DiscordApiBackoff as bo:
                self.assertEqual(bo.retry_after, 200000, 'Retry-After time must be equal to Retry-After set in header')
                self.assertFalse(bo.global_ratelimit, 'global_ratelimit must be False')
                raise bo

        self.assertTrue(djcache.set.called)
        args, kwargs = djcache.set.call_args
        self.assertEqual(args[0], 'DISCORD_BACKOFF_update_groups')
        self.assertTrue(datetime.datetime.strptime(args[1], manager.cache_time_format) > datetime.datetime.now())

    @mock.patch(MODULE_PATH + '.manager.cache')
    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._get_user_roles')
    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._group_name_to_id')
    @requests_mock.Mocker()
    def test_update_groups_global_backoff(self, name_to_id, user_groups, djcache, m):
        # Arrange
        groups = ['Member']
        user_groups.return_value = []
        name_to_id.return_value = '111'

        headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        user_id = 12345
        request_url = '{}/guilds/{}/members/{}/roles/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id, name_to_id.return_value)

        djcache.get.return_value = None  # No existing backoffs in cache

        m.put(request_url,
              request_headers=headers,
              headers={'Retry-After': '200000', 'X-RateLimit-Global': 'true'},
              status_code=429)

        # Act & Assert
        with self.assertRaises(manager.DiscordApiBackoff) as bo:
            try:
                DiscordOAuthManager.update_groups(user_id, groups, blocking=False)
            except manager.DiscordApiBackoff as bo:
                self.assertEqual(bo.retry_after, 200000, 'Retry-After time must be equal to Retry-After set in header')
                self.assertTrue(bo.global_ratelimit, 'global_ratelimit must be True')
                raise bo

        self.assertTrue(djcache.set.called)
        args, kwargs = djcache.set.call_args
        self.assertEqual(args[0], 'DISCORD_BACKOFF_GLOBAL')
        self.assertTrue(datetime.datetime.strptime(args[1], manager.cache_time_format) > datetime.datetime.now())
