from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=16, required = True)
    password = forms.CharField(widget=forms.PasswordInput())
    email   = forms.CharField(max_length=254, required = True)
    api_id  = forms.CharField(max_length=254, required = True)
    api_key = forms.CharField(max_length=254, required = True)