from django import forms

class UpdateKeyForm(forms.Form):
    api_id = forms.CharField(max_length=254, required = True)
    api_key = forms.CharField(max_length=254, required = True)
