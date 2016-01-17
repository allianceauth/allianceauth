from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator



class SignatureForm(forms.Form):
    sigtype = [('Wormhole', 'Wormhole'), ('Combat', 'Combat'), ('Data', 'Data'),
                         ('Relic', 'Relic')]
    status = [('Open', 'Open'), ('Started', 'Started'), ('Finished', 'Finished')]

    system = forms.CharField(max_length=254, required=True, label='System')
    ident = forms.CharField(max_length=254, required=True, label="ID")
    sigtype = forms.ChoiceField(choices=sigtype, required=True, label="Signiture Type")
    destination = forms.CharField(max_length=254, label="destination", required=True, initial="")
    status = forms.ChoiceField(choices=status, required=True, label="Status")
    notes = forms.CharField(max_length=254, label="Notes", required=False, initial="")
    
    
    
    
