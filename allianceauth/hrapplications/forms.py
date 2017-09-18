from django import forms
from django.utils.translation import ugettext_lazy as _


class HRApplicationCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, required=False, label=_("Comment"))


class HRApplicationSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label=_("Search String"))
