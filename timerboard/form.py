from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator



class TimerForm(forms.Form):
    structure_choices = [('POCO', 'POCO'), ('I-HUB', 'I-HUB'), ('POS[S]', 'POS[S]'),
                         ('POS[M]', 'POS[M]'), ('POS[L]', 'POS[L]'), ('Station', 'Station'), ('TCU', 'TCU'), ('Other', 'Other')]
    objective_choices = [('Friendly', 'Friendly'), ('Hostile', 'Hostile'), ('Neutral', 'Neutral')]

    details = forms.CharField(max_length=254, required=True, label='Details')
    system = forms.CharField(max_length=254, required=True, label="System")
    planet_moon = forms.CharField(max_length=254, label="Planet/Moon", required=False, initial="")
    structure = forms.ChoiceField(choices=structure_choices, required=True, label="Structure Type")
    objective = forms.ChoiceField(choices=objective_choices, required=True, label="Objective")
    days_left = forms.IntegerField(required=True, label="Days Remaining", validators=[MinValueValidator(0)])
    hours_left = forms.IntegerField(required=True, label="Hours Remaining", validators=[MinValueValidator(0), MaxValueValidator(23)])
    minutes_left = forms.IntegerField(required=True, label="Minutes Remaining", validators=[MinValueValidator(0), MaxValueValidator(59)])
    important = forms.BooleanField(label="Important", required=False)
    corp_timer = forms.BooleanField(label="Corp-Restricted", required=False)
