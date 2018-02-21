import logging
import datetime
from django import forms
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _

from .models import Timer

logger = logging.getLogger(__name__)


class TimerForm(forms.ModelForm):
    class Meta:
        model = Timer
        fields = ('details', 'system', 'planet_moon', 'structure', 'objective', 'important', 'corp_timer')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            # Do conversion from db datetime to days/hours/minutes
            # for appropriate fields
            current_time = timezone.now()
            td = kwargs['instance'].eve_time - current_time
            initial = kwargs.pop('initial', dict())
            if 'days_left' not in initial:
                initial.update({'days_left': td.days})
            if 'hours_left' not in initial:
                initial.update({'hours_left': td.seconds // 3600})
            if 'minutes_left' not in initial:
                initial.update({'minutes_left': td.seconds // 60 % 60})
            kwargs.update({'initial': initial})
        super(TimerForm, self).__init__(*args, **kwargs)

    structure_choices = [('POCO', 'POCO'),
                         ('I-HUB', 'I-HUB'),
                         ('POS[S]', 'POS[S]'),
                         ('POS[M]', 'POS[M]'),
                         ('POS[L]', 'POS[L]'),
                         ('Citadel[M]', 'Citadel[M]'),
                         ('Citadel[L]', 'Citadel[L]'),
                         ('Citadel[XL]', 'Citadel[XL]'),
                         ('Engineering Complex[M]', 'Engineering Complex[M]'),
                         ('Engineering Complex[L]', 'Engineering Complex[L]'),
                         ('Engineering Complex[XL]', 'Engineering Complex[XL]'),
                         ('Refinery[M]', 'Refinery[M]'),
                         ('Refinery[L]', 'Refinery[L]'),
                         ('Station', 'Station'),
                         ('TCU', 'TCU'),
                         ('Moon Mining Cycle', 'Moon Mining Cycle'),
                         (_('Other'), _('Other'))]
    objective_choices = [('Friendly', _('Friendly')),
                         ('Hostile', _('Hostile')),
                         ('Neutral', _('Neutral'))]

    details = forms.CharField(max_length=254, required=True, label=_('Details'))
    system = forms.CharField(max_length=254, required=True, label=_("System"))
    planet_moon = forms.CharField(max_length=254, label=_("Planet/Moon"), required=False, initial="")
    structure = forms.ChoiceField(choices=structure_choices, required=True, label=_("Structure Type"))
    objective = forms.ChoiceField(choices=objective_choices, required=True, label=_("Objective"))
    days_left = forms.IntegerField(required=True, label=_("Days Remaining"), validators=[MinValueValidator(0)])
    hours_left = forms.IntegerField(required=True, label=_("Hours Remaining"),
                                    validators=[MinValueValidator(0), MaxValueValidator(23)])
    minutes_left = forms.IntegerField(required=True, label=_("Minutes Remaining"),
                                      validators=[MinValueValidator(0), MaxValueValidator(59)])
    important = forms.BooleanField(label=_("Important"), required=False)
    corp_timer = forms.BooleanField(label=_("Corp-Restricted"), required=False)

    def save(self, commit=True):
        timer = super(TimerForm, self).save(commit=False)

        # Get character
        character = self.user.profile.main_character
        corporation = character.corporation
        logger.debug("Determined timer save request on behalf "
                     "of character {} corporation {}".format(character, corporation))
        # calculate future time
        future_time = datetime.timedelta(days=self.cleaned_data['days_left'], hours=self.cleaned_data['hours_left'],
                                         minutes=self.cleaned_data['minutes_left'])
        current_time = timezone.now()
        eve_time = current_time + future_time
        logger.debug(
            "Determined timer eve time is %s - current time %s, adding %s" % (eve_time, current_time, future_time))

        timer.eve_time = eve_time
        timer.eve_character = character
        timer.eve_corp = corporation
        timer.user = self.user
        if commit:
            timer.save()
        return timer
