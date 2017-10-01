import datetime
import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .form import TimerForm
from .models import Timer

logger = logging.getLogger(__name__)


class BaseTimerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    pass


class TimerView(BaseTimerView):
    template_name = 'timerboard/view.html'
    permission_required = 'auth.timer_view'

    def get(self, request):
        logger.debug("timer_view called by user {}".format(request.user))
        char = request.user.profile.main_character
        if char:
            corp = char.corporation
        else:
            corp = None
        base_query = Timer.objects.select_related('eve_character')
        render_items = {
            'timers': base_query.filter(corp_timer=False),
            'corp_timers': base_query.filter(corp_timer=True, eve_corp=corp),
            'future_timers': base_query.filter(corp_timer=False, eve_time__gte=timezone.now()),
            'past_timers': base_query.filter(corp_timer=False, eve_time__lt=timezone.now()),
        }

        return render(request, self.template_name, context=render_items)


class TimerManagementView(BaseTimerView):
    permission_required = 'auth.timer_management'
    index_redirect = 'timerboard:view'
    success_url = reverse_lazy(index_redirect)
    model = Timer
    form_class = TimerForm

    def get_timer(self, timer_id):
        return get_object_or_404(self.model, id=timer_id)


class AddUpdateMixin:
    def get_form_kwargs(self):
        """
        Inject the request user into the kwargs passed to the form
        """
        kwargs = super(AddUpdateMixin, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class AddTimerView(TimerManagementView, AddUpdateMixin, CreateView):
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        result = super(AddTimerView, self).form_valid(form)
        timer = self.object
        logger.info("Created new timer in {} at {} by user {}".format(timer.system, timer.eve_time, self.request.user))
        messages.success(self.request, _('Added new timer in %(system)s at %(time)s.') % {"system": timer.system,
                                                                                          "time": timer.eve_time})
        return result


class EditTimerView(TimerManagementView, AddUpdateMixin, UpdateView):
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        messages.success(self.request, _('Saved changes to the timer.'))
        return super(EditTimerView, self).form_valid(form)


class RemoveTimerView(TimerManagementView, DeleteView):
    pass
