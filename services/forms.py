from django import forms

class JabberBroadcastForm(forms.Form):
    group = forms.ChoiceField(widget=forms.Select)
    message = forms.CharField(widget=forms.Textarea)


class FleetFormatterForm(forms.Form):
    fleet_name = forms.CharField(label='Name of Fleet:', required=True)
    fleet_commander = forms.CharField(label='Fleet Commander:', required=True)
    fleet_comms = forms.CharField(label='Fleet Comms:', required=True)
    fleet_type = forms.CharField(label='Fleet Type:', required=True)
    ship_priorities = forms.CharField(label='Ship Priorities:', required=True)
    formup_location = forms.CharField(label='Formup Location:', required=True)
    formup_time = forms.CharField(label='Formup Time:', required=True)
    expected_duration = forms.CharField(label='Expected Duration:', required=True)
    purpose = forms.CharField(label='Purpose:', required=True)
    reimbursable = forms.ChoiceField(label='Reimbursable?*', choices=[('Yes', 'Yes'), ('No', 'No')], required=True)
    important = forms.ChoiceField(label='Important?*', choices=[('Yes', 'Yes'), ('No', 'No')], required=True)
    comments = forms.CharField(widget=forms.Textarea, required=False)

class DiscordForm(forms.Form):
    email = forms.CharField(label="Email Address", required=True)
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput)

class ServicePasswordForm(forms.Form):
    password = forms.CharField(label="Password", required=True)
    def clean_password(self):
        password = self.cleaned_data['password']
        if not len(password) >= 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password
