from django.contrib import admin
from django import forms
from allianceauth import hooks
from .models import NameFormatConfig


class NameFormatConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NameFormatConfigForm, self).__init__(*args, **kwargs)
        SERVICE_CHOICES = [(s.name, s.name) for h in hooks.get_hooks('services_hook') for s in [h()]]
        if self.instance.id:
            current_choice = (self.instance.service_name, self.instance.service_name)
            if current_choice not in SERVICE_CHOICES:
                SERVICE_CHOICES.append(current_choice)
        self.fields['service_name'] = forms.ChoiceField(choices=SERVICE_CHOICES)


class NameFormatConfigAdmin(admin.ModelAdmin):
    form = NameFormatConfigForm
    list_display = ('service_name', 'get_state_display_string')

    def get_state_display_string(self, obj):
        return ', '.join([state.name for state in obj.states.all()])
    get_state_display_string.short_description = 'States'


admin.site.register(NameFormatConfig, NameFormatConfigAdmin)
