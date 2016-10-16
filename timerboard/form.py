from __future__ import unicode_literals
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _


class TimerForm(forms.Form):
    structure_choices = [('POCO', 'POCO'), ('I-HUB', 'I-HUB'), ('POS[S]', 'POS[S]'),
                         ('POS[M]', 'POS[M]'), ('POS[L]', 'POS[L]'), ('Station', 'Station'), ('TCU', 'TCU'),
                         (_('Other'), _('Other'))]
    objective_choices = [('Friendly', _('Friendly')), ('Hostile', _('Hostile')), ('Neutral', _('Neutral'))]

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
