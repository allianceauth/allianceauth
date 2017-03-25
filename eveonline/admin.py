from __future__ import unicode_literals
from django.contrib import admin
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from eveonline.models import EveCharacter
from eveonline.models import EveAllianceInfo
from eveonline.models import EveCorporationInfo
from eveonline.managers import EveManager
from eveonline.providers import ObjectNotFound


class EveEntityForm(forms.ModelForm):
    id = forms.IntegerField(min_value=1)
    entity_type_name = None  # override in subclass
    entity_model_class = None

    def clean_id(self):
        try:
            assert getattr(EveManager, 'get_%s' % self.entity_type_name)(self.cleaned_data['id'])
        except (AssertionError, ObjectNotFound):
            raise forms.ValidationError('%s with ID %s not found.' % (self.entity_type_name, self.cleaned_data['id']))
        if self.entity_model_class.objects.filter(
                **{'%s_id' % self.entity_type_name: self.cleaned_data['id']}).exists():
            raise forms.ValidationError(
                '%s with ID %s already exists.' % (self.entity_type_name, self.cleaned_data['id']))
        return self.cleaned_data['id']

    def save(self, commit=True):
        return getattr(EveManager, 'create_%s' % self.entity_type_name)(self.cleaned_data['id'])

    def save_m2m(self):
        pass


class EveCharacterForm(EveEntityForm):
    entity_model_class = EveCharacter
    entity_type_name = 'character'

    class Meta:
        fields = ['id']
        model = EveCharacter


class EveCorporationForm(EveEntityForm):
    entity_model_class = EveCorporationInfo
    entity_type_name = 'corporation'

    class Meta:
        fields = ['id']
        model = EveCorporationInfo


class EveAllianceForm(EveEntityForm):
    entity_model_class = EveAllianceInfo
    entity_type_name = 'alliance'

    class Meta:
        fields = ['id']
        model = EveAllianceInfo


@admin.register(EveCorporationInfo)
class EveCorporationInfoAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if not obj or not obj.pk:
            return EveCorporationForm
        return super(EveCorporationInfoAdmin, self).get_form(request, obj=obj, **kwargs)


@admin.register(EveAllianceInfo)
class EveAllianceInfoAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if not obj or not obj.pk:
            return EveAllianceForm
        return super(EveAllianceInfoAdmin, self).get_form(request, obj=obj, **kwargs)


@admin.register(EveCharacter)
class EveCharacterAdmin(admin.ModelAdmin):
    search_fields = ['character_name', 'corporation_name', 'alliance_name', 'character_ownership__user__username']
    list_display = ('character_name', 'corporation_name', 'alliance_name', 'user', 'main_character')

    @staticmethod
    def user(obj):
        try:
            return obj.character_ownership.user
        except (AttributeError, ObjectDoesNotExist):
            return None

    @staticmethod
    def main_character(obj):
        try:
            return obj.character_ownership.user.profile.main_character
        except (AttributeError, ObjectDoesNotExist):
            return None

    def get_form(self, request, obj=None, **kwargs):
        if not obj or not obj.pk:
            return EveCharacterForm
        return super(EveCharacterAdmin, self).get_form(request, obj=obj, **kwargs)
