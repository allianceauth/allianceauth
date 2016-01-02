from django import forms
from django.conf import settings

from services.managers.eve_api_manager import EveApiManager
from eveonline.managers import EveManager

import logging

logger = logging.getLogger(__name__)

class UpdateKeyForm(forms.Form):
    api_id = forms.CharField(max_length=254, required=True, label="Key ID")
    api_key = forms.CharField(max_length=254, required=True, label="Verification Code")
    is_blue = forms.BooleanField(label="Blue to corp/alliance", required=False)

    def clean(self):
        if EveManager.check_if_api_key_pair_exist(self.cleaned_data['api_id']):
            logger.debug("UpdateKeyForm failed cleaning as API id %s already exists." % self.cleaned_data['api_id'])
            raise forms.ValidationError(u'API key already exist')

        check_blue = False
        try:
            check_blue = self.cleaned_data['is_blue']
        except:
            pass

        if check_blue:
            if settings.BLUE_API_ACCOUNT:
                if not EveApiManager.check_api_is_type_account(self.cleaned_data['api_id'],
                                                               self.cleaned_data['api_key']):
                    logger.debug("UpdateKeyForm failed cleaning as API id %s does not meet blue api key account requirement." % self.cleaned_data['api_id'])
                    raise forms.ValidationError(u'API not of type account')

            if not EveApiManager.check_blue_api_is_full(self.cleaned_data['api_id'],
                                                   self.cleaned_data['api_key']):
                logger.debug("UpdateKeyForm failed cleaning as API id %s does not meet minimum blue api access mask requirement." % self.cleaned_data['api_id'])
                raise forms.ValidationError(u'API supplied is too restricted. Minimum access mask is ' + str(settings.BLUE_API_MASK))

        else:
            if settings.MEMBER_API_ACCOUNT:
                if not EveApiManager.check_api_is_type_account(self.cleaned_data['api_id'],
                                                           self.cleaned_data['api_key']):
                    logger.debug("UpdateKeyForm failed cleaning as API id %s does not meet member api key account requirement." % self.cleaned_data['api_id'])
                    raise forms.ValidationError(u'API not of type account')

            if not EveApiManager.check_api_is_full(self.cleaned_data['api_id'],
                                                   self.cleaned_data['api_key']):
                logger.debug("UpdateKeyForm failed cleaning as API id %s does not meet minimum member api access mask requirement." % self.cleaned_data['api_id'])
                raise forms.ValidationError(u'API supplied is too restricted. Minimum access mask is ' + str(settings.MEMBER_API_MASK))

        return self.cleaned_data
