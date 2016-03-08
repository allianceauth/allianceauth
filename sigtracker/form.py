from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator



class SignatureForm(forms.Form):
    mass_status = [('More Than 50%', 'More Than 50%'), ('Less Than 50%', 'Less Than 50%'), ('Less Than 10%', 'Less Than 10%')]
    lifetime_status = [('More Than 24 Hours', 'More Than 24 Hours'), ('Less Than 24 Hours', 'Less Than 24 Hours'), ('Less Than 4 Hours', 'Less Than 4 Hours')]
    ships_size = [('Only Smallest', 'Only Smallest'), ('Up to Medium', 'Up to Medium'), ('Larger', 'Larger'), ('Very Large', 'Very Large')]


    system = forms.CharField(max_length=254, required=True, label='System')
    ident = forms.CharField(max_length=254, required=True, label="ID")
    lifetime_status = forms.ChoiceField(choices=lifetime_status, required=True, label="Lifetime Status")
    mass_status = forms.ChoiceField(choices=mass_status, required=True, label="Mass Status")
    ships_size = forms.ChoiceField(choices=ships_size, required=True, label="Ship Size")
    destination = forms.CharField(max_length=254, label="End Destination", required=True, initial="")
    through_dest = forms.CharField(max_length=254, label="Goes Through", required=True, initial="")
    notes = forms.CharField(max_length=254, label="Notes", required=False, initial="")
    



    
    
    
