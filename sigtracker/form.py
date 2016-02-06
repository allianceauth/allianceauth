from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator



class SignatureForm(forms.Form):
    sigtype = [('Wormhole', 'Wormhole'), ('Combat', 'Combat'), ('Data', 'Data'),
              ('Relic', 'Relic'), ('Gas', 'Gas'), ('Ore', 'Ore')]
    status = [('Open', 'Open'), ('Started', 'Started'), ('Finished', 'Finished'), ('Life cycle has not begun', 'Life cycle has not begun'),
             ('Probably wont last another day', 'Probably wont last another day'), ('Reaching the end of its natural lifetime', 'Reaching the end of its natural lifetime'),
             ('Has not yet had its stability significantly disrupted', 'Has not yet had its stability significantly disrupted'),
             ('Has had its stability reduced, but not to a critical degree yet', 'Has had its stability reduced, but not to a critical degree yet')
             ('This wormhole has had its stability critically disrupted', 'This wormhole has had its stability critically disrupted')]

    system = forms.CharField(max_length=254, required=True, label='System')
    ident = forms.CharField(max_length=254, required=True, label="ID")
    sigtype = forms.ChoiceField(choices=sigtype, required=True, label="Signature Type")
    destination = forms.CharField(max_length=254, label="destination", required=True, initial="")
    status = forms.ChoiceField(choices=status, required=True, label="Status")
    notes = forms.CharField(max_length=254, label="Notes", required=False, initial="")
    
    
    
    
