from django import forms
from django.conf import settings

from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo

class SelectCorpForm(forms.Form):
    alliance = EveAllianceInfo.objects.get(alliance_id=settings.ALLIANCE_ID)
    alliancecorps = EveCorporationInfo.objects.filter(alliance=alliance)
    corpnamelist = [(int(corp.corporation_id), str(corp.corporation_name)) for corp in alliancecorps]
    corpnamelist.sort(key=lambda tup: tup[1])
    corpid = forms.ChoiceField(corpnamelist, required=True, label="Corporation")

class CorputilsSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Search characters...'}))
