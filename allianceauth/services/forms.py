from django import forms
from django.utils.translation import ugettext_lazy as _


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


class ServicePasswordForm(forms.Form):
    password = forms.CharField(label=_("Password"), required=True, widget=forms.PasswordInput())

    def clean_password(self):
        password = self.cleaned_data['password']
        if not len(password) >= 8:
            raise forms.ValidationError(_("Password must be at least 8 characters long."))
        return password


class ServicePasswordModelForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), required=True, widget=forms.PasswordInput())

    def clean_password(self):
        password = self.cleaned_data['password']
        if not len(password) >= 8:
            raise forms.ValidationError(_("Password must be at least 8 characters long."))
        return password

    def save(self, commit=True):
        svc_obj = super(ServicePasswordModelForm, self).save(commit=False)
        svc_obj.update_password(self.cleaned_data['password'])
        if commit:
            svc_obj.save()
        return svc_obj
