from django import forms


class SrpFleetMainForm(forms.Form):
    fleet_name = forms.CharField(required=True, label="Fleet Name")
    fleet_time = forms.DateTimeField(required=True, label="Fleet Time")
    fleet_doctrine = forms.CharField(required=True, label="Fleet Doctrine")


class SrpFleetUserRequestForm(forms.Form):
    killboard_link = forms.CharField(required=True, label="ZKillboard Link")
    additional_info = forms.CharField(required=False, label="Additional Info")


class SrpFleetUpdateCostForm(forms.Form):
    srp_total_amount = forms.IntegerField(required=True, label="Total SRP Amount")


class SrpFleetMainUpdateForm(forms.Form):
    fleet_aar_link = forms.CharField(required=True, label="After Action Report Link")
