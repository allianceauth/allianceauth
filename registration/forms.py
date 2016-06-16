from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import re

import logging

logger = logging.getLogger(__name__)

class RegistrationForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=30, required=True)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(), required=True)
    password_again = forms.CharField(label=_('Password Again'), widget=forms.PasswordInput(), required=True)
    email = forms.CharField(label=_('Email'), max_length=254, required=True)
    email_again = forms.CharField(label=_('Email Again'), max_length=254, required=True)

    def clean(self):
        if ' ' in self.cleaned_data['username']:
            logger.debug("RegistrationForm username contains spaces. Raising ValidationError. Username: %s" % self.cleaned_data['username'])
            raise forms.ValidationError(u'Username cannot contain a space')

        # We attempt to get the user object if we succeed we know email as been used
        try:
            User.objects.get(email=self.cleaned_data['email'])
            logger.debug("RegistrationForm email already registered. Raising ValidationError")
            raise forms.ValidationError(u'Email as already been used')
        except:
            pass

        if not re.match("^\w+$", self.cleaned_data['username']):
            logger.debug("RegistrationForm username contains non-alphanumeric characters. Raising ValueError. Username: %s" % self.cleaned_data['username'])
            raise forms.ValidationError(u'Username contains illegal characters')

        if 'password' in self.cleaned_data and 'password_again' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password_again']:
                logger.debug("RegistrationForm password mismatch. Raising ValueError")
                raise forms.ValidationError(u'Passwords do not match')

        if 'email' in self.cleaned_data and 'email_again' in self.cleaned_data:
            if self.cleaned_data['email'] != self.cleaned_data['email_again']:
                logger.debug("RegistrationForm email mismatch. Raising ValidationError")
                raise forms.ValidationError(u'Emails do not match')

        return self.cleaned_data
