from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator



class SignatureForm(forms.Form):
    sigtype = [('Wormhole', 'Wormhole'), ('Combat', 'Combat'), ('Data', 'Data'),
              ('Relic', 'Relic'), ('Gas', 'Gas'), ('Ore', 'Ore')]
    status = [('Open', 'Open'), ('Started', 'Started'), ('Finished', 'Finished'), ('Life cycle has not begun', 'Life cycle has not begun'),
             ('Probably wont last another day', 'Probably wont last another day'), ('End of its natural lifetime', 'End of its natural lifetime'),
             ('stability not significantly disrupted', 'stability not significantly disrupted'),
             ('Stability reduced not critical degree yet', 'Stability reduced not critical degree yet'),
             ('Wormhole stability critically disrupted', 'Wormhole stability critically disrupted')]

    system = forms.CharField(max_length=254, required=True, label='System')
    ident = forms.CharField(max_length=254, required=True, label="ID")
    sigtype = forms.ChoiceField(choices=sigtype, required=True, label="Signature Type")
    destination = forms.CharField(max_length=254, label="destination", required=True, initial="")
    status = forms.ChoiceField(choices=status, required=True, label="Status")
    notes = forms.CharField(max_length=254, label="Notes", required=False, initial="")
    
    
    
    
