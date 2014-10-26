from django import forms


class HRApplicationForm(forms.Form):
    character_name = forms.CharField(max_length=254, required=True, label="Main Character Name")
    full_api_id = forms.CharField(max_length=254, required=True, label="API ID")
    full_api_key = forms.CharField(max_length=254, required=True, label="API Verification Code")
    preferred_corp = forms.CharField(max_length=254, required=True, label="Preferred Corp")
    is_a_spi = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')], required=True, label='Are you a spy?')
    about = forms.CharField(widget=forms.Textarea, required=False, label="About You")
    extra = forms.CharField(widget=forms.Textarea, required=False, label="Extra Application Info")