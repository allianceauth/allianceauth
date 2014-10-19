from django import forms
from django.contrib.auth.models import Group


class JabberBroadcastForm(forms.Form):
    allchoices = []
    allchoices.append(('all', 'all'))
    for group in Group.objects.all():
        allchoices.append((str(group.name), str(group.name)))
    group = forms.ChoiceField(choices=allchoices, widget=forms.Select)
    message = forms.CharField(widget = forms.Textarea)