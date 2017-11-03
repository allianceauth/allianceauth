import logging

from allianceauth.services.forms import ServicePasswordModelForm
from allianceauth.services.abstract import BaseCreatePasswordServiceAccountView, BaseDeactivateServiceAccountView, \
    BaseResetPasswordServiceAccountView, BaseSetPasswordServiceAccountView

from .models import MumbleUser

logger = logging.getLogger(__name__)


class MumblePasswordForm(ServicePasswordModelForm):
    class Meta:
        model = MumbleUser
        fields = ('password',)


class MumbleViewMixin:
    service_name = 'mumble'
    model = MumbleUser
    permission_required = 'mumble.access_mumble'


class CreateAccountMumbleView(MumbleViewMixin, BaseCreatePasswordServiceAccountView):
    pass


class DeleteMumbleView(MumbleViewMixin, BaseDeactivateServiceAccountView):
    pass


class ResetPasswordMumbleView(MumbleViewMixin, BaseResetPasswordServiceAccountView):
    pass


class SetPasswordMumbleView(MumbleViewMixin, BaseSetPasswordServiceAccountView):
    form_class = MumblePasswordForm
