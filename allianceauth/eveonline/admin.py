from django import forms
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from .providers import ObjectNotFound

from .models import EveAllianceInfo
from .models import EveCharacter
from .models import EveCorporationInfo


class EveEntityExistsError(forms.ValidationError):
    def __init__(self, entity_type_name, id):
        super(EveEntityExistsError, self).__init__(
            message='{} with ID {} already exists.'.format(entity_type_name, id))


class EveEntityNotFoundError(forms.ValidationError):
    def __init__(self, entity_type_name, id):
        super(EveEntityNotFoundError, self).__init__(
            message='{} with ID {} not found.'.format(entity_type_name, id))


class EveEntityForm(forms.ModelForm):
    id = forms.IntegerField(min_value=1)
    entity_model_class = None

    def clean_id(self):
        raise NotImplementedError()

    def save(self, commit=True):
        raise NotImplementedError()

    def save_m2m(self):
        pass


class EveCharacterForm(EveEntityForm):
    entity_type_name = 'character'

    def clean_id(self):
        try:
            assert self.Meta.model.provider.get_character(self.cleaned_data['id'])
        except (AssertionError, ObjectNotFound):
            raise EveEntityNotFoundError(self.entity_type_name, self.cleaned_data['id'])
        if self.Meta.model.objects.filter(character_id=self.cleaned_data['id']).exists():
            raise EveEntityExistsError(self.entity_type_name, self.cleaned_data['id'])
        return self.cleaned_data['id']

    def save(self, commit=True):
        return self.Meta.model.objects.create_character(self.cleaned_data['id'])

    class Meta:
        fields = ['id']
        model = EveCharacter


class EveCorporationForm(EveEntityForm):
    entity_type_name = 'corporation'

    def clean_id(self):
        try:
            assert self.Meta.model.provider.get_corporation(self.cleaned_data['id'])
        except (AssertionError, ObjectNotFound):
            raise EveEntityNotFoundError(self.entity_type_name, self.cleaned_data['id'])
        if self.Meta.model.objects.filter(corporation_id=self.cleaned_data['id']).exists():
            raise EveEntityExistsError(self.entity_type_name, self.cleaned_data['id'])
        return self.cleaned_data['id']

    def save(self, commit=True):
        return self.Meta.model.objects.create_corporation(self.cleaned_data['id'])

    class Meta:
        fields = ['id']
        model = EveCorporationInfo


class EveAllianceForm(EveEntityForm):
    entity_type_name = 'alliance'

    def clean_id(self):
        try:
            assert self.Meta.model.provider.get_alliance(self.cleaned_data['id'])
        except (AssertionError, ObjectNotFound):
            raise EveEntityNotFoundError(self.entity_type_name, self.cleaned_data['id'])
        if self.Meta.model.objects.filter(alliance_id=self.cleaned_data['id']).exists():
            raise EveEntityExistsError(self.entity_type_name, self.cleaned_data['id'])
        return self.cleaned_data['id']

    def save(self, commit=True):
        return self.Meta.model.objects.create_alliance(self.cleaned_data['id'])

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
