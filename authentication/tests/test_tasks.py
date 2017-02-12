from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase
from django.contrib.auth.models import Group, Permission

from alliance_auth.tests.auth_utils import AuthUtils

from authentication.tasks import disable_member, disable_user


class AuthenticationTasksTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        self.none_user = AuthUtils.create_user('none_user', disconnect_signals=True)

    @mock.patch('services.signals.transaction')
    def test_disable_member(self, transaction):
        # Inert signals action
        transaction.on_commit.side_effect = lambda fn: fn()

        # Add permission
        perm = Permission.objects.create(codename='test_perm', name='test perm', content_type_id=1)

        # Add public group
        pub_group = Group.objects.create(name="A Public group")
        pub_group.authgroup.internal = False
        pub_group.authgroup.public = True
        pub_group.save()

        # Setup member
        self.member.user_permissions.add(perm)
        self.member.groups.add(pub_group)

        # Pre assertion
        self.assertIn(pub_group, self.member.groups.all())
        self.assertGreater(len(self.member.groups.all()), 1)

        # Act
        disable_member(self.member)

        # Assert
        self.assertIn(pub_group, self.member.groups.all())
        # Everything but the single public group wiped
        self.assertEqual(len(self.member.groups.all()), 1)
        # All permissions wiped
        self.assertEqual(len(self.member.user_permissions.all()), 0)

    @mock.patch('services.signals.transaction')
    def test_disable_user(self, transaction):
        # Inert signals action
        transaction.on_commit.side_effect = lambda fn: fn()

        # Add permission
        perm = Permission.objects.create(codename='test_perm', name='test perm', content_type_id=1)

        # Add public group
        pub_group = Group.objects.create(name="A Public group")
        pub_group.authgroup.internal = False
        pub_group.authgroup.public = True
        pub_group.save()

        # Setup member
        self.member.user_permissions.add(perm)
        self.member.groups.add(pub_group)

        # Pre assertion
        self.assertIn(pub_group, self.member.groups.all())
        self.assertGreater(len(self.member.groups.all()), 1)

        # Act
        disable_user(self.member)

        # Assert
        # All groups wiped
        self.assertEqual(len(self.member.groups.all()), 0)
        # All permissions wiped
        self.assertEqual(len(self.member.user_permissions.all()), 0)
