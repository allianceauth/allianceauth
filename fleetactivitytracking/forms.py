from __future__ import unicode_literals
from django import forms
from optimer.models import OpTimer
from django.utils.translation import ugettext_lazy as _


class FatlinkForm(forms.Form):
    fatname = forms.CharField(label=_('Name of fat-link'), required=True)
    duration = forms.IntegerField(label=_("Duration of fat-link"), required=True, initial=30, min_value=1,
                                  max_value=2147483647)
    fleet = forms.ModelChoiceField(label=_("Fleet"), queryset=OpTimer.objects.all().order_by('operation_name'))
