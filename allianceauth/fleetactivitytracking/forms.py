
from django import forms
from django.utils.translation import ugettext_lazy as _

from allianceauth.optimer.models import OpTimer


class FatlinkForm(forms.Form):
    fatname = forms.CharField(label=_('Name of fat-link'), required=True)
    duration = forms.IntegerField(label=_("Duration of fat-link"), required=True, initial=30, min_value=1,
                                  max_value=2147483647)
    fleet = forms.ModelChoiceField(label=_("Fleet"), queryset=OpTimer.objects.all().order_by('operation_name'))
