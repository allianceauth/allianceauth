from django import forms

class HRApplicationCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, required=False, label="Comment", max_length=254)

class HRApplicationSearchForm(forms.Form):
    search_string = forms.CharField(max_length=254, required=True, label="Search String")
