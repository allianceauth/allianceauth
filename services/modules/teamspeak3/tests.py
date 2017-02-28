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
from django.db.models import signals

from alliance_auth.tests.auth_utils import AuthUtils

from .auth_hooks import Teamspeak3Service
from .models import Teamspeak3User, AuthTS, TSgroup
from .tasks import Teamspeak3Tasks
from .signals import m2m_changed_authts_group, post_save_authts, post_delete_authts

MODULE_PATH = 'services.modules.teamspeak3'


def add_permissions():
    permission = Permission.objects.get(codename='access_teamspeak3')
    members = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
    blues = Group.objects.get(name=settings.DEFAULT_BLUE_GROUP)
    AuthUtils.add_permissions_to_groups([permission], [members, blues])


class Teamspeak3HooksTestCase(TestCase):
    def setUp(self):
        # Inert signals before setup begins
        with mock.patch(MODULE_PATH + '.signals.trigger_all_ts_update') as trigger_all_ts_update:
            self.member = 'member_user'
            member = AuthUtils.create_member(self.member)
            Teamspeak3User.objects.create(user=member, uid=self.member, perm_key='123ABC')
            self.blue = 'blue_user'
            blue = AuthUtils.create_blue(self.blue)
            Teamspeak3User.objects.create(user=blue, uid=self.blue, perm_key='456DEF')
            self.none_user = 'none_user'
            none_user = AuthUtils.create_user(self.none_user)

            ts_member_group = TSgroup.objects.create(ts_group_id=1, ts_group_name='Member')
            ts_blue_group = TSgroup.objects.create(ts_group_id=2, ts_group_name='Blue')
            m2m_member_group = AuthTS.objects.create(auth_group=member.groups.all()[0])
            m2m_member_group.ts_group.add(ts_member_group)
            m2m_member_group.save()
            m2m_blue_group = AuthTS.objects.create(auth_group=blue.groups.all()[0])
            m2m_blue_group.ts_group.add(ts_blue_group)
            m2m_blue_group.save()
            self.service = Teamspeak3Service
            add_permissions()

    def test_has_account(self):
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(Teamspeak3Tasks.has_account(member))
        self.assertTrue(Teamspeak3Tasks.has_account(blue))
        self.assertFalse(Teamspeak3Tasks.has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        blue = User.objects.get(username=self.blue)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertTrue(service.service_active_for_user(blue))
        self.assertFalse(service.service_active_for_user(none_user))

    @mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager')
    def test_update_all_groups(self, manager):
        instance = manager.return_value.__enter__.return_value
        service = self.service()
        service.update_all_groups()
        # Check member and blue user have groups updated
        self.assertTrue(instance.update_groups.called)
        self.assertEqual(instance.update_groups.call_count, 2)

    def test_update_groups(self):
        # Check member has Member group updated
        with mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager') as manager:
            instance = manager.return_value.__enter__.return_value
            service = self.service()
            member = User.objects.get(username=self.member)
            service.update_groups(member)
            self.assertTrue(instance.update_groups.called)
            args, kwargs = instance.update_groups.call_args
            # update_groups(user.teamspeak3.uid, groups)
            self.assertEqual({'Member': 1}, args[1])  # Check groups
            self.assertEqual(self.member, args[0])  # Check uid

        # Check none user does not have groups updated
        with mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager') as manager:
            service = self.service()
            none_user = User.objects.get(username=self.none_user)
            service.update_groups(none_user)
            self.assertFalse(manager.return_value.__enter__.return_value.update_user_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager')
    def test_validate_user(self, manager):
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.teamspeak3)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        Teamspeak3User.objects.create(user=none_user, uid='abc123', perm_key='132ACB')
        service.validate_user(none_user)
        self.assertTrue(manager.return_value.__enter__.return_value.delete_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            none_teamspeak3 = User.objects.get(username=self.none_user).teamspeak3

    @mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager')
    def test_delete_user(self, manager):
        member = User.objects.get(username=self.member)

        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        self.assertTrue(manager.return_value.__enter__.return_value.delete_user.called)
        with self.assertRaises(ObjectDoesNotExist):
            teamspeak3_user = User.objects.get(username=self.member).teamspeak3

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/en/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn(urls.reverse('auth_deactivate_teamspeak3'), response)
        self.assertIn(urls.reverse('auth_reset_teamspeak3_perm'), response)

        # Test register becomes available
        member.teamspeak3.delete()
        member = User.objects.get(username=self.member)
        request.user = member
        response = service.render_services_ctrl(request)
        self.assertIn(urls.reverse('auth_activate_teamspeak3'), response)


class Teamspeak3ViewsTestCase(TestCase):
    def setUp(self):
        # Inert signals before setup begins
        with mock.patch(MODULE_PATH + '.signals.trigger_all_ts_update') as trigger_all_ts_update:
            self.member = AuthUtils.create_member('auth_member')
            self.member.set_password('password')
            self.member.email = 'auth_member@example.com'
            self.member.save()
            AuthUtils.add_main_character(self.member, 'auth_member', '12345', corp_id='111', corp_name='Test Corporation')
            self.blue_user = AuthUtils.create_blue('auth_blue')
            self.blue_user.set_password('password')
            self.blue_user.email = 'auth_blue@example.com'
            self.blue_user.save()
            AuthUtils.add_main_character(self.blue_user, 'auth_blue', '92345', corp_id='111', corp_name='Test Corporation')

            ts_member_group = TSgroup.objects.create(ts_group_id=1, ts_group_name='Member')
            ts_blue_group = TSgroup.objects.create(ts_group_id=2, ts_group_name='Blue')
            m2m_member = AuthTS.objects.create(auth_group=Group.objects.get(name='Member'))
            m2m_member.ts_group.add(ts_member_group)
            m2m_member.save()
            m2m_blue = AuthTS.objects.create(auth_group=Group.objects.get(name='Blue'))
            m2m_blue.ts_group.add(ts_blue_group)
            m2m_blue.save()
            add_permissions()

    def login(self, user=None, password=None):
        if user is None:
            user = self.member
        self.client.login(username=user.username, password=password if password else 'password')

    @mock.patch(MODULE_PATH + '.forms.Teamspeak3Manager')
    @mock.patch(MODULE_PATH + '.views.Teamspeak3Manager')
    def test_activate(self, manager, forms_manager):
        self.login()
        expected_username = 'auth_member'
        instance = manager.return_value.__enter__.return_value
        instance.add_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('auth_activate_teamspeak3'))

        self.assertTrue(instance.add_user.called)
        teamspeak3_user = Teamspeak3User.objects.get(user=self.member)
        self.assertTrue(teamspeak3_user.uid)
        self.assertTrue(teamspeak3_user.perm_key)
        self.assertRedirects(response, urls.reverse('auth_verify_teamspeak3'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.forms.Teamspeak3Manager')
    @mock.patch(MODULE_PATH + '.views.Teamspeak3Manager')
    def test_activate_blue(self, manager, forms_manager):
        self.login(self.blue_user)
        expected_username = 'auth_blue'
        instance = manager.return_value.__enter__.return_value
        instance.add_blue_user.return_value = (expected_username, 'abc123')

        response = self.client.get(urls.reverse('auth_activate_teamspeak3'))

        self.assertTrue(instance.add_blue_user.called)
        teamspeak3_user = Teamspeak3User.objects.get(user=self.blue_user)
        self.assertTrue(teamspeak3_user.uid)
        self.assertTrue(teamspeak3_user.perm_key)
        self.assertRedirects(response, urls.reverse('auth_verify_teamspeak3'), target_status_code=200)

    @mock.patch(MODULE_PATH + '.forms.Teamspeak3Manager')
    @mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager')
    def test_verify_submit(self, manager, forms_manager):
        self.login()
        expected_username = 'auth_member'

        forms_instance = manager.return_value.__enter__.return_value
        forms_instance._get_userid.return_value = '1234'

        Teamspeak3User.objects.update_or_create(user=self.member, defaults={'uid': '1234', 'perm_key': '5678'})
        data = {'username': 'auth_member'}

        response = self.client.post(urls.reverse('auth_verify_teamspeak3'), data)

        self.assertRedirects(response, urls.reverse('auth_services'), target_status_code=200)
        self.assertTrue(manager.return_value.__enter__.return_value.update_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager')
    def test_deactivate(self, manager):
        self.login()
        Teamspeak3User.objects.create(user=self.member, uid='some member')

        response = self.client.get(urls.reverse('auth_deactivate_teamspeak3'))

        self.assertTrue(manager.return_value.__enter__.return_value.delete_user.called)
        self.assertRedirects(response, expected_url=urls.reverse('auth_services'), target_status_code=200)
        with self.assertRaises(ObjectDoesNotExist):
            teamspeak3_user = User.objects.get(pk=self.member.pk).teamspeak3

    @mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager')
    @mock.patch(MODULE_PATH + '.views.Teamspeak3Manager')
    def test_reset_perm(self, manager, tasks_manager):
        self.login()
        Teamspeak3User.objects.create(user=self.member, uid='some member')

        manager.return_value.__enter__.return_value.generate_new_permissionkey.return_value = "valid_member", "123abc"

        response = self.client.get(urls.reverse('auth_reset_teamspeak3_perm'))

        self.assertRedirects(response, urls.reverse('auth_services'), target_status_code=200)
        ts3_user = Teamspeak3User.objects.get(uid='valid_member')
        self.assertEqual(ts3_user.uid, 'valid_member')
        self.assertEqual(ts3_user.perm_key, '123abc')
        self.assertTrue(tasks_manager.return_value.__enter__.return_value.update_groups.called)

    @mock.patch(MODULE_PATH + '.tasks.Teamspeak3Manager')
    @mock.patch(MODULE_PATH + '.views.Teamspeak3Manager')
    def test_reset_perm_blue(self, manager, tasks_manager):
        self.login(self.blue_user)
        Teamspeak3User.objects.create(user=self.blue_user, uid='some member')

        manager.return_value.__enter__.return_value.generate_new_blue_permissionkey.return_value = ("valid_blue",
                                                                                                    "123abc")

        response = self.client.get(urls.reverse('auth_reset_teamspeak3_perm'))

        self.assertRedirects(response, urls.reverse('auth_services'), target_status_code=200)
        ts3_user = Teamspeak3User.objects.get(uid='valid_blue')
        self.assertEqual(ts3_user.uid, 'valid_blue')
        self.assertEqual(ts3_user.perm_key, '123abc')
        self.assertTrue(tasks_manager.return_value.__enter__.return_value.update_groups.called)


class Teamspeak3SignalsTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')

        # Suppress signals action while setting up
        with mock.patch(MODULE_PATH + '.signals.trigger_all_ts_update') as trigger_all_ts_update:
            ts_member_group = TSgroup.objects.create(ts_group_id=1, ts_group_name='Member')
            self.m2m_member = AuthTS.objects.create(auth_group=Group.objects.get(name='Member'))
            self.m2m_member.ts_group.add(ts_member_group)
            self.m2m_member.save()

    def test_m2m_signal_registry(self):
        """
        Test that the m2m signal has been registered
        """
        registered_functions = [r[1]() for r in signals.m2m_changed.receivers]
        self.assertIn(m2m_changed_authts_group, registered_functions)

    def test_post_save_signal_registry(self):
        """
        Test that the post_save signal has been registered
        """
        registered_functions = [r[1]() for r in signals.post_save.receivers]
        self.assertIn(post_save_authts, registered_functions)

    def test_post_delete_signal_registry(self):
        """
        Test that the post_delete signal has been registered
        """
        registered_functions = [r[1]() for r in signals.post_delete.receivers]
        self.assertIn(post_delete_authts, registered_functions)

    @mock.patch(MODULE_PATH + '.signals.transaction')
    @mock.patch(MODULE_PATH + '.signals.trigger_all_ts_update')
    def test_m2m_changed_authts_group(self, trigger_all_ts_update, transaction):

        # Overload transaction.on_commit so everything happens synchronously
        transaction.on_commit = lambda fn: fn()

        new_group = TSgroup.objects.create(ts_group_id=99, ts_group_name='new TS group')
        self.m2m_member.ts_group.add(new_group)
        self.m2m_member.save()  # Triggers signal

        self.assertTrue(trigger_all_ts_update.called)

    @mock.patch(MODULE_PATH + '.signals.transaction')
    @mock.patch(MODULE_PATH + '.signals.trigger_all_ts_update')
    def test_post_save_authts(self, trigger_all_ts_update, transaction):

        # Overload transaction.on_commit so everything happens synchronously
        transaction.on_commit = lambda fn: fn()

        AuthTS.objects.create(auth_group=Group.objects.create(name='Test Group'))  # Trigger signal (AuthTS creation)

        self.assertTrue(trigger_all_ts_update.called)

    @mock.patch(MODULE_PATH + '.signals.transaction')
    @mock.patch(MODULE_PATH + '.signals.trigger_all_ts_update')
    def test_post_delete_authts(self, trigger_all_ts_update, transaction):
        # Overload transaction.on_commit so everything happens synchronously
        transaction.on_commit = lambda fn: fn()

        self.m2m_member.delete()  # Trigger delete signal

        self.assertTrue(trigger_all_ts_update.called)
