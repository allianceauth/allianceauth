from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo

class CorputilsSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label="", widget=forms.TextInput(attrs={'placeholder': _('Search characters...')}))
