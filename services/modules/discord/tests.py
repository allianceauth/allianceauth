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
from .manager import DiscordOAuthManager

import requests_mock
import datetime

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


class DiscordManagerTestCase(TestCase):
    def setUp(self):
        pass

    def test__sanitize_groupname(self):
        test_group_name = ' Group Name_Test_'
        group_name = DiscordOAuthManager._sanitize_groupname(test_group_name)

        self.assertEqual(group_name, 'GroupName_Test')

    def test_generate_Bot_add_url(self):
        from . import manager
        bot_add_url = DiscordOAuthManager.generate_bot_add_url()

        auth_url = manager.AUTH_URL
        real_bot_add_url = '{}?client_id=appid&scope=bot&permissions={}'.format(auth_url, manager.BOT_PERMISSIONS)
        self.assertEqual(bot_add_url, real_bot_add_url)

    def test_generate_oauth_redirect_url(self):
        from . import manager
        import urllib
        import sys
        oauth_url = DiscordOAuthManager.generate_oauth_redirect_url()

        self.assertIn(manager.AUTH_URL, oauth_url)
        self.assertIn('+'.join(manager.SCOPES), oauth_url)
        self.assertIn(settings.DISCORD_APP_ID, oauth_url)
        if sys.version_info[0] < 3:
            # Py2
            self.assertIn(urllib.quote_plus(settings.DISCORD_CALLBACK_URL), oauth_url)
        else: # Py3
            self.assertIn(urllib.parse.quote_plus(settings.DISCORD_CALLBACK_URL), oauth_url)

    @mock.patch(MODULE_PATH + '.manager.OAuth2Session')
    def test__process_callback_code(self, oauth):
        from . import manager
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
        from . import manager
        import json

        # Arrange
        oauth_token.return_value = {'access_token': 'accesstoken'}

        headers = {'accept': 'application/json', 'authorization': 'Bearer accesstoken'}

        m.register_uri('POST',
                       manager.DISCORD_URL + '/invites/'+str(settings.DISCORD_INVITE_CODE),
                       request_headers=headers,
                       text='{}')

        m.register_uri('GET',
                       manager.DISCORD_URL + "/users/@me",
                       request_headers=headers,
                       text=json.dumps({'id': "123456"}))

        # Act
        return_value = DiscordOAuthManager.add_user('abcdef')

        # Assert
        self.assertEqual(return_value, '123456')
        self.assertEqual(m.call_count, 2)

    @requests_mock.Mocker()
    def test_delete_user(self, m):
        from . import manager
        import json

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
        from . import manager
        import json
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

    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._get_groups')
    @requests_mock.Mocker()
    def test_update_groups(self, group_cache, m):
        from . import manager
        import json

        # Arrange
        groups = ['Member', 'Blue', 'Special Group']

        group_cache.return_value = [{'id': 111, 'name': 'Member'},
                                    {'id': 222, 'name': 'Blue'},
                                    {'id': 333, 'name': 'SpecialGroup'},
                                    {'id': 444, 'name': 'NotYourGroup'}]

        headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        user_id = 12345
        request_url = '{}/guilds/{}/members/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id)

        m.patch(request_url,
                request_headers=headers)

        # Act
        DiscordOAuthManager.update_groups(user_id, groups)

        # Assert
        self.assertEqual(len(m.request_history), 1, 'Must be one HTTP call made')
        history = json.loads(m.request_history[0].text)
        self.assertIn('roles', history, "'The request must send JSON object with the 'roles' key")
        self.assertIn(111, history['roles'], 'The group id 111 must be added to the request')
        self.assertIn(222, history['roles'], 'The group id 222 must be added to the request')
        self.assertIn(333, history['roles'], 'The group id 333 must be added to the request')
        self.assertNotIn(444, history['roles'], 'The group id 444 must NOT be added to the request')

    @mock.patch(MODULE_PATH + '.manager.cache')
    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._get_groups')
    @requests_mock.Mocker()
    def test_update_groups_backoff(self, group_cache, djcache, m):
        from . import manager

        # Arrange
        groups = ['Member']
        group_cache.return_value = [{'id': 111, 'name': 'Member'}]

        headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        user_id = 12345
        request_url = '{}/guilds/{}/members/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id)

        djcache.get.return_value = None  # No existing backoffs in cache

        m.patch(request_url,
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
    @mock.patch(MODULE_PATH + '.manager.DiscordOAuthManager._get_groups')
    @requests_mock.Mocker()
    def test_update_groups_global_backoff(self, group_cache, djcache, m):
        from . import manager

        # Arrange
        groups = ['Member']
        group_cache.return_value = [{'id': 111, 'name': 'Member'}]

        headers = {'content-type': 'application/json', 'authorization': 'Bot ' + settings.DISCORD_BOT_TOKEN}
        user_id = 12345
        request_url = '{}/guilds/{}/members/{}'.format(manager.DISCORD_URL, settings.DISCORD_GUILD_ID, user_id)

        djcache.get.return_value = None  # No existing backoffs in cache

        m.patch(request_url,
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
