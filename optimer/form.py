from __future__ import unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _


class opForm(forms.Form):
    doctrine = forms.CharField(max_length=254, required=True, label=_('Doctrine'))
    system = forms.CharField(max_length=254, required=True, label=_("System"))
    location = forms.CharField(max_length=254, required=True, label=_("Location"))
    start = forms.DateTimeField(required=True, label=_("Start Time"))
    duration = forms.CharField(max_length=254, required=True, label=_("Duration"))
    operation_name = forms.CharField(max_length=254, required=True, label=_("Operation Name"))
    fc = forms.CharField(max_length=254, required=True, label=_("Fleet Commander"))
    details = forms.CharField(max_length=254, required=False, label=_("Extra Details"))
