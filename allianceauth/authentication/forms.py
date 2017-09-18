from django import forms
from django.utils.translation import ugettext_lazy as _


class RegistrationForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=254, required=True)
