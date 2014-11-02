from django import forms

from eveonline.models import EveCorporationInfo


class HRApplicationForm(forms.Form):
    allchoices = []
    for corp in EveCorporationInfo.objects.all():
        allchoices.append((str(corp.corporation_id), str(corp.corporation_name)))

    character_name = forms.CharField(max_length=254, required=True, label="Main Character Name")
    full_api_id = forms.CharField(max_length=254, required=True, label="API ID")
    full_api_key = forms.CharField(max_length=254, required=True, label="API Verification Code")
    corp = forms.ChoiceField(choices=allchoices, required=True, label="Corp")
    is_a_spi = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')], required=True, label='Are you a spy?')
    about = forms.CharField(widget=forms.Textarea, required=False, label="About You")
    extra = forms.CharField(widget=forms.Textarea, required=False, label="Extra Application Info")