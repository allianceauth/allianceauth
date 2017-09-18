from django import forms
from django.utils.translation import ugettext_lazy as _


class SrpFleetMainForm(forms.Form):
    fleet_name = forms.CharField(required=True, label=_("Fleet Name"))
    fleet_time = forms.DateTimeField(required=True, label=_("Fleet Time"))
    fleet_doctrine = forms.CharField(required=True, label=_("Fleet Doctrine"))


class SrpFleetUserRequestForm(forms.Form):
    additional_info = forms.CharField(required=False, max_length=25, label=_("Additional Info"))
    killboard_link = forms.CharField(
        label=_("zKillboard Link"),
        max_length=255,
        required=True

    )

    def clean_killboard_link(self):
        data = self.cleaned_data['killboard_link']
        if "zkillboard.com" not in data:
            raise forms.ValidationError(_("Invalid Link. Please use zKillboard.com"))
        return data


class SrpFleetMainUpdateForm(forms.Form):
    fleet_aar_link = forms.CharField(required=True, label=_("After Action Report Link"))
