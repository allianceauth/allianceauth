from django import forms


class UpdateKeyForm(forms.Form):
    api_id = forms.CharField(max_length=254, required=True, label="Key ID")
    api_key = forms.CharField(max_length=254, required=True, label="Verification Code")