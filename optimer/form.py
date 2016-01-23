from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator



class opForm(forms.Form):
    
    doctrine = forms.CharField(max_length=254, required=True, label='Doctrine')
    system = forms.CharField(max_length=254, required=True, label="System")
    location = forms.CharField(max_length=254, required=True, label="Location")
    start_time = forms.CharField(max_length=254, required=True, label="Start Time")    
    end_time = forms.CharField(max_length=254, required=True, label="End Time")
    operation_name = forms.CharField(max_length=254, required=True, label="Operation Name")
    fc = forms.CharField(max_length=254, required=True, label="Fleet Commander")
    details = forms.CharField(max_length=254, required=False, label="Extra Details")
    
    
    
    
    
