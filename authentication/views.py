from __future__ import unicode_literals
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from eveonline.managers import EveManager
from eveonline.models import EveCharacter
from authentication.models import AuthServicesInfo
from authentication.forms import LoginForm, RegistrationForm
from django.contrib.auth.models import User
from django.contrib import messages
from esi.decorators import token_required
import logging

logger = logging.getLogger(__name__)


def login_user(request):
    logger.debug("login_user called by user %s" % request.user)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        logger.debug("Request of type POST, received form, valid: %s" % form.is_valid())
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            logger.debug("Authentication attempt with supplied credentials. Received user %s" % user)
            if user is not None:
                if user.is_active:
                    logger.info("Successful login attempt from user %s" % user)
                    login(request, user)
                    redirect_to = request.POST.get('next', request.GET.get('next', ''))
                    if not redirect_to:
                        redirect_to = 'auth_dashboard'
                    return redirect(redirect_to)
                else:
                    logger.info("Login attempt failed for user %s: user marked inactive." % user)
                    messages.warning(request, 'Your account has been disabled.')
            else:
                logger.info("Failed login attempt: provided username %s" % form.cleaned_data['username'])
                messages.error(request, 'Username/password invalid.')
            return render(request, 'public/login.html', context={'form': form})
    else:
        logger.debug("Providing new login form.")
        form = LoginForm()

    return render(request, 'public/login.html', context={'form': form})


def logout_user(request):
    logger.debug("logout_user called by user %s" % request.user)
    temp_user = request.user
    logout(request)
    logger.info("Successful logout for user %s" % temp_user)
    return redirect("auth_index")


def register_user_view(request):
    logger.debug("register_user_view called by user %s" % request.user)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():

            if not User.objects.filter(username=form.cleaned_data['username']).exists():
                user = User.objects.create_user(form.cleaned_data['username'],
                                                form.cleaned_data['email'], form.cleaned_data['password'])

                user.save()
                logger.info("Created new user %s" % user)
                messages.warning(request, 'Add an API key to set up your account.')
                return redirect("auth_dashboard")

            else:
                logger.error("Unable to register new user: username %s already exists." % form.cleaned_data['username'])
                return render(request, 'public/register.html', context={'form': form, 'error': True})
        else:
            logger.debug("Registration form invalid. Returning for user %s to make corrections." % request.user)

    else:
        logger.debug("Returning blank registration form.")
        form = RegistrationForm()

    return render(request, 'public/register.html', context={'form': form})


def index_view(request):
    logger.debug("index_view called by user %s" % request.user)
    return render(request, 'public/index.html')


@login_required
def dashboard_view(request):
    logger.debug("dashboard_view called by user %s" % request.user)
    render_items = {'characters': EveManager.get_characters_by_owner_id(request.user.id),
                    'authinfo': AuthServicesInfo.objects.get_or_create(user=request.user)[0]}
    return render(request, 'registered/dashboard.html', context=render_items)


@login_required
def help_view(request):
    logger.debug("help_view called by user %s" % request.user)
    return render(request, 'registered/help.html')

@token_required(new=True)
def sso_login(request, token):
    try:
        char = EveCharacter.objects.get(character_id=token.character_id)
        if char.user:
            if char.user.is_active:
                login(request, char.user)
                token.user = char.user
                token.save()
                return redirect(dashboard_view)
            else:
                messages.error(request, 'Your account has been disabled.')
        else:
            messages.warning(request, 'Authenticated character has no owning account. Please log in with username and password.')
    except EveCharacter.DoesNotExist:
        messages.error(request, 'No account exists with the authenticated character. Please create an account first.')
    return redirect(login_user)
