from django_webtest import WebTest
from django import urls
from django.contrib.auth.models import Group, Permission

from allianceauth.tests.auth_utils import AuthUtils


class PermissionsToolViewsTestCase(WebTest):
    def setUp(self):
        self.member = AuthUtils.create_member('auth_member')
        AuthUtils.add_main_character(self.member, 'test character', '1234', '2345', 'test corp', 'testc')
        self.member.email = 'auth_member@example.com'
        self.member.save()
        self.none_user = AuthUtils.create_user('none_user', disconnect_signals=True)
        self.none_user2 = AuthUtils.create_user('none_user2', disconnect_signals=True)
        self.none_user3 = AuthUtils.create_user('none_user3', disconnect_signals=True)

        self.no_perm_user = AuthUtils.create_user('no_perm_user', disconnect_signals=True)

        AuthUtils.disconnect_signals()
        self.no_perm_group = Group.objects.create(name="No Permission Group")

        self.test_group = Group.objects.create(name="Test group")

        self.test_group.user_set.add(self.none_user)
        self.test_group.user_set.add(self.none_user2)
        self.test_group.user_set.add(self.none_user3)

        self.permission = Permission.objects.get_by_natural_key(codename='audit_permissions',
                                                                app_label='permissions_tool',
                                                                model='permissionstool')

        self.test_group.permissions.add(self.permission)
        self.member.user_permissions.add(self.permission)
        AuthUtils.connect_signals()

    def test_menu_item(self):
        self.app.set_user(self.member)
        response = self.app.get(urls.reverse('permissions_tool:overview'))

        response_content = response.content.decode('utf-8')

        self.assertInHTML('<li><a class="active" href="/permissions/overview/">'
                          '<i class="fa fa-key fa-id-card"></i> Permissions Audit</a></li>', response_content)

    def test_permissions_overview(self):
        self.app.set_user(self.member)

        response = self.app.get(urls.reverse('permissions_tool:overview'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('permissions_tool/overview.html')
        self.assertContains(response, self.permission.codename)
        self.assertContains(response, self.permission.content_type.app_label)
        self.assertContains(response, self.permission.content_type.model)

        tested_context = False
        # Test the context
        for perm in response.context['permissions']:
            if perm['permission'] == self.permission:
                tested_context = True
                self.assertIn('users', perm)
                self.assertEqual(perm['users'], 1)
                self.assertIn('groups', perm)
                self.assertEqual(perm['groups'], 1)
                self.assertIn('group_users', perm)
                self.assertEqual(perm['group_users'], 3)
                break
        self.assertTrue(tested_context)

    def test_permissions_overview_perms(self):
        # Ensure permission effectively denys access
        self.app.set_user(self.no_perm_user)

        response = self.app.get(urls.reverse('permissions_tool:overview'))

        self.assertEqual(response.status_code, 302)

    def test_permissions_audit(self):
        self.client.force_login(self.member)

        response = self.client.get(urls.reverse('permissions_tool:audit',
                                                kwargs={
                                                    'app_label': self.permission.content_type.app_label,
                                                    'model': self.permission.content_type.model,
                                                    'codename': self.permission.codename,
                                                }))

        self.assertTemplateUsed('permissions_tool/audit.html')
        self.assertTemplateUsed('permissions_tool/audit_row.html')

        self.assertContains(response, self.permission.codename)
        self.assertContains(response, self.none_user)
        self.assertContains(response, self.none_user3)
        self.assertContains(response, self.test_group)

        self.assertNotContains(response, self.no_perm_user)

    def test_permissions_audit_perms(self):
        # Ensure permission effectively denys access
        self.app.set_user(self.no_perm_user)

        response = self.app.get(urls.reverse('permissions_tool:audit',
                                                kwargs={
                                                    'app_label': self.permission.content_type.app_label,
                                                    'model': self.permission.content_type.model,
                                                    'codename': self.permission.codename,
                                                }))

        self.assertEqual(response.status_code, 302)
