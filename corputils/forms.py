from django import forms


class CorputilsSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label="Search String")
