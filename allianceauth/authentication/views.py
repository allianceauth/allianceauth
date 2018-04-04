import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import signing
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from esi.decorators import token_required
from esi.models import Token
from registration.backends.hmac.views import RegistrationView as BaseRegistrationView, \
    ActivationView as BaseActivationView, REGISTRATION_SALT
from registration.signals import user_registered

from .models import CharacterOwnership
from .forms import RegistrationForm

logger = logging.getLogger(__name__)


@login_required
@token_required(scopes=settings.LOGIN_TOKEN_SCOPES)
def main_character_change(request, token):
    logger.debug("main_character_change called by user %s for character %s" % (request.user, token.character_name))
    try:
        co = CharacterOwnership.objects.get(character__character_id=token.character_id, user=request.user)
    except CharacterOwnership.DoesNotExist:
        if not CharacterOwnership.objects.filter(character__character_id=token.character_id).exists():
            co = CharacterOwnership.objects.create_by_token(token)
        else:
            messages.error(request, 'Cannot change main character to %(char)s: character owned by a different account.' % ({'char': token.character_name}))
            co = None
    if co:
        request.user.profile.main_character = co.character
        request.user.profile.save(update_fields=['main_character'])
        messages.success(request, _('Changed main character to %(char)s') % {"char": co.character})
        logger.info('Changed user %(user)s main character to %(char)s' % ({'user': request.user, 'char': co.character}))
    return redirect("authentication:dashboard")


@token_required(new=True, scopes=settings.LOGIN_TOKEN_SCOPES)
def add_character(request, token):
    if CharacterOwnership.objects.filter(character__character_id=token.character_id).filter(
            owner_hash=token.character_owner_hash).filter(user=request.user).exists():
        messages.success(request, _('Added %(name)s to your account.'% ({'name': token.character_name})))
    else:
        messages.error(request, _('Failed to add %(name)s to your account: they already have an account.' % ({'name': token.character_name})))
    return redirect('authentication:dashboard')


"""
Override the HMAC two-step registration view to accommodate the three-step registration required.
Step 1: OAuth token to create user and profile.
Step 2: Get email and send activation link (but do not save email).
Step 3: Get link, save email and activate.

Step 1 is necessary to automatically assign character ownership and a main character, both of which require a saved User
model - this means the ensuing registration form cannot create the user because it already exists.

Email is not saved to the user model in Step 2 as a way of differentiating users who have not yet completed registration
(is_active=False) and users who have been disabled by an admin (is_active=False, email present).

Because of this, the email address needs to be assigned in Step 3 after clicking the link, which means the link must
have the email address embedded much like the username. Key creation and decoding is overridden to support this action.
"""


# Step 1
@token_required(new=True, scopes=settings.LOGIN_TOKEN_SCOPES)
def sso_login(request, token):
    user = authenticate(token=token)
    if user:
        token.user = user
        if Token.objects.exclude(pk=token.pk).equivalent_to(token).require_valid().exists():
            token.delete()
        else:
            token.save()
        if user.is_active:
            login(request, user)
            return redirect(request.POST.get('next', request.GET.get('next', 'authentication:dashboard')))
        elif not user.email:
            # Store the new user PK in the session to enable us to identify the registering user in Step 2
            request.session['registration_uid'] = user.pk
            # Go to Step 2
            return redirect('registration_register')
    messages.error(request, _('Unable to authenticate as the selected character.'))
    return redirect(settings.LOGIN_URL)


# Step 2
class RegistrationView(BaseRegistrationView):
    form_class = RegistrationForm
    success_url = 'authentication:dashboard'

    def get_success_url(self, user):
        if not getattr(settings, 'REGISTRATION_VERIFY_EMAIL', True):
            return 'authentication:dashboard', (), {}
        return super().get_success_url(user)

    def dispatch(self, request, *args, **kwargs):
        # We're storing a key in the session to pass user information from OAuth response. Make sure it's there.
        if not self.request.session.get('registration_uid', None) or not User.objects.filter(
                pk=self.request.session.get('registration_uid')).exists():
            messages.error(self.request, _('Registration token has expired.'))
            return redirect(settings.LOGIN_URL)
        if not getattr(settings, 'REGISTRATION_VERIFY_EMAIL', True):
            # Keep the request so the user can be automagically logged in.
            setattr(self, 'request', request)
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def register(self, form):
        user = User.objects.get(pk=self.request.session.get('registration_uid'))
        user.email = form.cleaned_data['email']
        user_registered.send(self.__class__, user=user, request=self.request)
        if getattr(settings, 'REGISTRATION_VERIFY_EMAIL', True):
            # Go to Step 3
            self.send_activation_email(user)
        else:
            user.is_active = True
            user.save()
            login(self.request, user, 'allianceauth.authentication.backends.StateBackend')
        return user

    def get_activation_key(self, user):
        return signing.dumps(obj=[getattr(user, User.USERNAME_FIELD), user.email], salt=REGISTRATION_SALT)

    def get_email_context(self, activation_key):
        context = super(RegistrationView, self).get_email_context(activation_key)
        context['url'] = context['site'].domain + reverse('registration_activate', args=[activation_key])
        return context


# Step 3
class ActivationView(BaseActivationView):
    def validate_key(self, activation_key):
        try:
            dump = signing.loads(activation_key, salt=REGISTRATION_SALT,
                                 max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400)
            return dump
        except signing.BadSignature:
            return None

    def activate(self, *args, **kwargs):
        dump = self.validate_key(kwargs.get('activation_key'))
        if dump:
            user = self.get_user(dump[0])
            if user:
                user.email = dump[1]
                user.is_active = True
                user.save()
                return user
        return False


def registration_complete(request):
    messages.success(request, _('Sent confirmation email. Please follow the link to confirm your email address.'))
    return redirect('authentication:login')


def activation_complete(request):
    messages.success(request, _('Confirmed your email address. Please login to continue.'))
    return redirect('authentication:dashboard')


def registration_closed(request):
    messages.error(request, _('Registraion of new accounts it not allowed at this time.'))
    return redirect('authentication:login')
