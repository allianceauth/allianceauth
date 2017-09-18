from django import forms
from django.utils.translation import ugettext_lazy as _


class JabberBroadcastForm(forms.Form):
    group = forms.ChoiceField(label=_('Group'), widget=forms.Select)
    message = forms.CharField(label=_('Message'), widget=forms.Textarea)
