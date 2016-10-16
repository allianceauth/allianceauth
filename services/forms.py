from __future__ import unicode_literals
from django import forms
from services.managers.teamspeak3_manager import Teamspeak3Manager
from django.utils.translation import ugettext_lazy as _


class JabberBroadcastForm(forms.Form):
    group = forms.ChoiceField(label=_('Group'), widget=forms.Select)
    message = forms.CharField(label=_('Message'), widget=forms.Textarea)


class FleetFormatterForm(forms.Form):
    fleet_name = forms.CharField(label=_('Name of Fleet:'), required=True)
    fleet_commander = forms.CharField(label=_('Fleet Commander:'), required=True)
    fleet_comms = forms.CharField(label=_('Fleet Comms:'), required=True)
    fleet_type = forms.CharField(label=_('Fleet Type:'), required=True)
    ship_priorities = forms.CharField(label=_('Ship Priorities:'), required=True)
    formup_location = forms.CharField(label=_('Formup Location:'), required=True)
    formup_time = forms.CharField(label=_('Formup Time:'), required=True)
    expected_duration = forms.CharField(label=_('Expected Duration:'), required=True)
    purpose = forms.CharField(label=_('Purpose:'), required=True)
    reimbursable = forms.ChoiceField(label=_('Reimbursable?*'), choices=[(_('Yes'), _('Yes')), (_('No'), _('No'))],
                                     required=True)
    important = forms.ChoiceField(label=_('Important?*'), choices=[(_('Yes'), _('Yes')), (_('No'), _('No'))],
                                  required=True)
    comments = forms.CharField(label=_('Comments'), widget=forms.Textarea, required=False)


class DiscordForm(forms.Form):
    email = forms.CharField(label=_("Email Address"), required=True)
    password = forms.CharField(label=_("Password"), required=True, widget=forms.PasswordInput)
    update_avatar = forms.BooleanField(label=_("Update Avatar"), required=False, initial=True)


class ServicePasswordForm(forms.Form):
    password = forms.CharField(label=_("Password"), required=True)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not len(password) >= 8:
            raise forms.ValidationError(_("Password must be at least 8 characters long."))
        return password


class TeamspeakJoinForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        if Teamspeak3Manager._get_userid(self.cleaned_data['username']):
            return self.cleaned_data
        raise forms.ValidationError(_("Unable to locate user %s on server") % self.cleaned_data['username'])
