from django import forms



class SrpFleetMainForm(forms.Form):
    fleet_name = forms.CharField(required=True, label="Fleet Name")
    fleet_time = forms.DateTimeField(required=True, label="Fleet Time")
    fleet_doctrine = forms.CharField(required=True, label="Fleet Doctrine")


class SrpFleetUserRequestForm(forms.Form):
    additional_info = forms.CharField(required=False, label="Additional Info")
    killboard_link = forms.CharField(
        label="zKillboard Link",
        max_length=255,
        required=True

    )

    def clean_killboard_link(self):
        data = self.cleaned_data['killboard_link']
        if "zkillboard.com" not in data:
            raise forms.ValidationError("Invalid Link. Please use zKillboard.com")
        return data


class SrpFleetUpdateCostForm(forms.Form):
    srp_total_amount = forms.IntegerField(required=True, label="Total SRP Amount")


class SrpFleetMainUpdateForm(forms.Form):
    fleet_aar_link = forms.CharField(required=True, label="After Action Report Link")
