from django_webtest import WebTest
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Permission, User
from django.conf import settings

from datetime import timedelta

from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.eveonline.models import EveCorporationInfo

from .models import Timer
from .form import TimerForm


class TimerboardViewsTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        corp = EveCorporationInfo.objects.create(corporation_id='2345', corporation_name='test corp',
                                                 corporation_ticker='testc', member_count=24)
        other_corp = EveCorporationInfo.objects.create(corporation_id='9345', corporation_name='other test corp',
                                                       corporation_ticker='testd', member_count=1)
        self.user = AuthUtils.create_user('test_user')
        AuthUtils.add_main_character(self.user, 'test character', '1234', '2345', 'test corp', 'testc')
        self.user = User.objects.get_by_natural_key('test_user')
        character = self.user.profile.main_character
        self.other_user = AuthUtils.create_user('other_test_user')
        AuthUtils.add_main_character(self.other_user, 'test character 2', '9234', '9345', 'other test corp', 'testd')
        self.other_user = User.objects.get_by_natural_key('other_test_user')
        other_character = self.other_user.profile.main_character

        self.timer = Timer.objects.create(
            details='details',
            system='system',
            planet_moon='planet_moon',
            structure='structure',
            objective='objective',
            eve_time=timezone.now() + timedelta(days=30),
            important=True,
            corp_timer=False,
            eve_character=character,
            eve_corp=character.corporation,
            user=self.user,
        )
        self.corp_timer = Timer.objects.create(
            details='details',
            system='system',
            planet_moon='planet_moon',
            structure='structure',
            objective='objective',
            eve_time=timezone.now() + timedelta(days=30),
            important=False,
            corp_timer=True,
            eve_character=character,
            eve_corp=character.corporation,
            user=self.user,
        )
        self.other_corp_timer = Timer.objects.create(
            details='details',
            system='system',
            planet_moon='planet_moon',
            structure='structure',
            objective='objective',
            eve_time=timezone.now() + timedelta(days=30),
            important=False,
            corp_timer=True,
            eve_character=other_character,
            eve_corp=other_character.corporation,
            user=self.user,
        )
        self.expired_timer = Timer.objects.create(
            details='details',
            system='system',
            planet_moon='planet_moon',
            structure='structure',
            objective='objective',
            eve_time=timezone.now() - timedelta(days=30),
            important=True,
            corp_timer=False,
            eve_character=character,
            eve_corp=character.corporation,
            user=self.user,
        )

        self.view_permission = Permission.objects.get(codename='timer_view')
        self.edit_permission = Permission.objects.get(codename='timer_management')

        self.view_url = reverse('timerboard:view')
        self.add_url = reverse('timerboard:add')
        self.edit_url_name = 'timerboard:edit'
        self.delete_url_name = 'timerboard:delete'

    def test_timer_view(self):
        self.user.user_permissions.add(self.view_permission)

        self.app.set_user(self.user)

        response = self.app.get(self.view_url)

        context = response.context[-1]

        timers = context['timers']
        corp_timers = context['corp_timers']
        future_timers = context['future_timers']
        past_timers = context['past_timers']

        self.assertTemplateUsed(response, 'timerboard/view.html')

        self.assertIn(self.timer, timers)
        self.assertIn(self.expired_timer, timers)
        self.assertNotIn(self.corp_timer, timers)
        self.assertNotIn(self.other_corp_timer, timers)

        self.assertNotIn(self.timer, corp_timers)
        self.assertNotIn(self.expired_timer, corp_timers)
        self.assertIn(self.corp_timer, corp_timers)
        self.assertNotIn(self.other_corp_timer, corp_timers)

        self.assertIn(self.timer, future_timers)
        self.assertNotIn(self.expired_timer, future_timers)
        self.assertNotIn(self.corp_timer, future_timers)
        self.assertNotIn(self.other_corp_timer, future_timers)

        self.assertNotIn(self.timer, past_timers)
        self.assertIn(self.expired_timer, past_timers)
        self.assertNotIn(self.corp_timer, past_timers)
        self.assertNotIn(self.other_corp_timer, past_timers)

    def test_timer_view_permission(self):
        self.client.force_login(self.user)
        response = self.app.get(self.view_url)
        self.assertRedirects(response, expected_url=reverse(settings.LOGIN_URL) + '?next=' + self.view_url)

    def test_timer_view_login(self):
        response = self.app.get(self.view_url)
        self.assertRedirects(response, expected_url=reverse(settings.LOGIN_URL) + '?next=' + self.view_url)

    def test_add_timer_get(self):
        self.user.user_permissions.add(self.edit_permission)
        self.app.set_user(self.user)

        response = self.app.get(self.add_url)

        self.assertTemplateUsed(response, 'timerboard/timer_create_form.html')

        context = response.context[-1]

        self.assertIs(TimerForm, type(context['form']))

    def test_add_timer_form_error(self):
        self.user.user_permissions.add(self.edit_permission)
        self.app.set_user(self.user)
        page = self.app.post(self.add_url)
        page = page.forms['add-timer-form'].submit()
        self.assertContains(page, "This field is required.")

    def test_add_timer_post(self):
        self.user.user_permissions.add(self.edit_permission)
        self.user.user_permissions.add(self.view_permission)

        self.app.set_user(self.user)

        page = self.app.post(self.add_url)
        form = page.forms['add-timer-form']

        form['details'] = 'details'
        form['system'] = 'jita'
        form['planet_moon'] = '4-4'
        form['structure'] = TimerForm.structure_choices[0][0]
        form['objective'] = TimerForm.objective_choices[0][0]
        form['days_left'] = 1
        form['hours_left'] = 2
        form['minutes_left'] = 3
        form['important'] = True
        form['corp_timer'] = False

        response = form.submit()

        self.assertRedirects(response, self.view_url)

        self.assertTrue(Timer.objects.filter(system='jita', details='details').exists())

    def test_edit_timer_get(self):
        self.user.user_permissions.add(self.edit_permission)
        self.app.set_user(self.user)

        response = self.app.get(reverse(self.edit_url_name, args=[self.timer.id]))
        context = response.context[-1]
        form = context['form']
        data = form.instance

        self.assertTemplateUsed(response, 'timerboard/timer_update_form.html')
        self.assertIs(TimerForm, type(form))
        self.assertEqual(data, self.timer)

    def test_edit_timer_post(self):
        self.user.user_permissions.add(self.edit_permission)
        self.user.user_permissions.add(self.view_permission)

        self.app.set_user(self.user)

        page = self.app.post(reverse(self.edit_url_name, args=[self.timer.id]))
        form = page.forms['add-timer-form']

        form['details'] = 'detailsUNIQUE'
        form['system'] = 'jita'
        form['planet_moon'] = '4-4'
        form['structure'] = TimerForm.structure_choices[0][0]
        form['objective'] = TimerForm.objective_choices[0][0]
        form['days_left'] = 1
        form['hours_left'] = 2
        form['minutes_left'] = 3
        form['important'] = True
        form['corp_timer'] = False

        response = form.submit()

        self.assertRedirects(response, self.view_url)

        self.assertTrue(Timer.objects.filter(system='jita', details='detailsUNIQUE').exists())

    def test_delete_timer_get(self):
        self.user.user_permissions.add(self.edit_permission)
        self.app.set_user(self.user)

        response = self.app.get(reverse(self.delete_url_name, args=[self.timer.id]))

        self.assertTemplateUsed(response, 'timerboard/timer_confirm_delete.html')

        self.assertContains(response, 'Are you sure you want to delete timer "'+str(self.timer))
