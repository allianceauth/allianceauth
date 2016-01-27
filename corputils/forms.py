from django import forms
from django.conf import settings

from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo

class CorputilsSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Search characters...'}))
