from django import forms
from services.managers.eve_api_manager import EveApiManager

class UpdateKeyForm(forms.Form):
    api_id = forms.CharField(max_length=254, required=True, label="Key ID")
    api_key = forms.CharField(max_length=254, required=True, label="Verification Code")

    def clean(self):
        if not EveApiManager.check_api_is_type_account(self.cleaned_data['api_id'],
                                                       self.cleaned_data['api_key']):
                raise forms.ValidationError(u'API not of type account')

        return self.cleaned_data