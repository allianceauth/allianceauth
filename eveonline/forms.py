from __future__ import unicode_literals
from django import forms
from django.conf import settings

from services.managers.eve_api_manager import EveApiManager
from eveonline.managers import EveManager
from eveonline.models import EveApiKeyPair
import evelink

import logging

logger = logging.getLogger(__name__)


class UpdateKeyForm(forms.Form):
    api_id = forms.CharField(max_length=254, required=True, label="Key ID")
    api_key = forms.CharField(max_length=254, required=True, label="Verification Code")

    def __init__(self, user, *args, **kwargs):
        super(UpdateKeyForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_api_id(self):
        try:
            api_id = int(self.cleaned_data['api_id'])
            return api_id
        except:
            raise forms.ValidationError("API ID must be a number")

    def clean(self):
        if 'api_id' not in self.cleaned_data or 'api_key' not in self.cleaned_data:
            # need to check if api_id and vcode in cleaned_data because
            # if they fail, they get removed from the dict but this method still happens
            return self.cleaned_data

        if EveManager.check_if_api_key_pair_exist(self.cleaned_data['api_id']):
            logger.debug("UpdateKeyForm failed cleaning as API id %s already exists." % self.cleaned_data['api_id'])
            if EveApiKeyPair.objects.get(api_id=self.cleaned_data['api_id']).user:
                # allow orphaned APIs to proceed to SSO validation upon re-entry
                raise forms.ValidationError('API key already exist')
        if settings.REJECT_OLD_APIS and not EveManager.check_if_api_key_pair_is_new(
                        self.cleaned_data['api_id'],
                        settings.REJECT_OLD_APIS_MARGIN):
            raise forms.ValidationError('API key is too old. Please create a new key')
        try:
            EveApiManager.validate_api(self.cleaned_data['api_id'], self.cleaned_data['api_key'], self.user)
            return self.cleaned_data
        except EveApiManager.ApiValidationError as e:
            raise forms.ValidationError(str(e))
        except evelink.api.APIError as e:
            logger.debug("Got error code %s while validating API %s" % (e.code, self.cleaned_data['api_id']))
            raise forms.ValidationError('Error while checking API key (%s)' % e.code)
