from django import forms


class TimerForm(forms.Form):
    structure_choices = [('POCO', 'POCO'), ('I-HUB', 'I-HUB'), ('POS[S]', 'POS[S]'),
                         ('POS[M]', 'POS[M]'), ('POS[L]', 'POS[L]'), ('Station', 'Station'), ('Other', 'Other')]
    fleet_type_choices = [('Armor', 'Armor'), ('Shield', 'Shield'), ('Other', 'Other')]

    name = forms.CharField(max_length=254, required=True, label='Fleet Name')
    system = forms.CharField(max_length=254, required=True, label="System")
    planet_moon = forms.CharField(max_length=254, label="Planet/Moon", required=False, initial="")
    structure = forms.ChoiceField(choices=structure_choices, required=True, label="Structure Type")
    fleet_type = forms.ChoiceField(choices=fleet_type_choices, required=True, label="Fleet Type")
    eve_time = forms.DateTimeField(required=True, label="Eve Time")
    important = forms.BooleanField(label="Important", required=False)