from django import forms

from services.managers.eve_api_manager import EveApiManager
from eveonline.managers import EveManager


class UpdateKeyForm(forms.Form):
    api_id = forms.CharField(max_length=254, required=True, label="Key ID")
    api_key = forms.CharField(max_length=254, required=True, label="Verification Code")
    is_blue = forms.BooleanField(label="Blue to alliance", required=False)

    def clean(self):
        if EveManager.check_if_api_key_pair_exist(self.cleaned_data['api_id']):
            raise forms.ValidationError(u'API key already exist')

        check_blue = False
        try:
            check_blue = self.cleaned_data['is_blue']
        except:
            pass

        if not check_blue:
            if not EveApiManager.check_api_is_type_account(self.cleaned_data['api_id'],
                                                           self.cleaned_data['api_key']):
                raise forms.ValidationError(u'API not of type account')

            if not EveApiManager.check_api_is_full(self.cleaned_data['api_id'],
                                                   self.cleaned_data['api_key']):
                raise forms.ValidationError(u'API supplied is not a full api key')

        return self.cleaned_data