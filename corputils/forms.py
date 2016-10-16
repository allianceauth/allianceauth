from __future__ import unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _


class CorputilsSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label="",
                                    widget=forms.TextInput(attrs={'placeholder': _('Search characters...')}))
