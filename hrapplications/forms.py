from django import forms
from django.conf import settings

from eveonline.models import EveCorporationInfo

class HRApplicationForm(forms.Form):
    allchoices = []

    if settings.IS_CORP:
        corp = EveCorporationInfo.objects.get(corporation_id=settings.CORP_ID)
        allchoices.append((str(corp.corporation_id), str(corp.corporation_name)))
    else:
        for corp in EveCorporationInfo.objects.all():
            if corp.alliance is not None:
                if corp.alliance.alliance_id == settings.ALLIANCE_ID:
                    allchoices.append((str(corp.corporation_id), str(corp.corporation_name)))

    character_name = forms.CharField(max_length=254, required=True, label="Main Character Name")
    full_api_id = forms.CharField(max_length=254, required=True, label="API ID")
    full_api_key = forms.CharField(max_length=254, required=True, label="API Verification Code")
    corp = forms.ChoiceField(choices=allchoices, required=True, label="Corp")
    is_a_spi = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')], required=True, label='Are you a spy?')
    about = forms.CharField(widget=forms.Textarea, required=False, label="About You")
    extra = forms.CharField(widget=forms.Textarea, required=False, label="Extra Application Info")


class HRApplicationCommentForm(forms.Form):
    app_id = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
    comment = forms.CharField(widget=forms.Textarea, required=False, label="Comment", max_length=254)


class HRApplicationSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label="Search String")
