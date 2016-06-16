from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _


class SignatureForm(forms.Form):
    mass_status = [(_('More Than 50%'), _('More Than 50%')), (_('Less Than 50%'), _('Less Than 50%')), (_('Less Than 10%'), _('Less Than 10%'))]
    lifetime_status = [(_('More Than 24 Hours'), _('More Than 24 Hours')), (_('Less Than 24 Hours'), _('Less Than 24 Hours')), (_('Less Than 4 Hours'), _('Less Than 4 Hours'))]
    ships_size = [(_('Only Smallest'), _('Only Smallest')), (_('Up to Medium'), _('Up to Medium')), (_('Larger'), _('Larger')), (_('Very Large'), _('Very Large'))]


    system = forms.CharField(max_length=254, required=True, label=_('System'))
    ident = forms.CharField(max_length=254, required=True, label=_("ID"))
    lifetime_status = forms.ChoiceField(choices=lifetime_status, required=True, label=_("Lifetime Status"))
    mass_status = forms.ChoiceField(choices=mass_status, required=True, label=_("Mass Status"))
    ships_size = forms.ChoiceField(choices=ships_size, required=True, label=_("Ship Size"))
    destination = forms.CharField(max_length=254, label=_("End Destination"), required=True, initial="")
    through_dest = forms.CharField(max_length=254, label=_("Goes Through"), required=True, initial="")
    notes = forms.CharField(max_length=254, label=_("Notes"), required=False, initial="")
    



    
    
    
