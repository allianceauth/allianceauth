from django.conf.urls import include
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required


def user_has_main_character(user):
    return bool(user.profile.main_character)


def decorate_url_patterns(urls, decorator):
    url_list, app_name, namespace = include(urls)

    def process_patterns(url_patterns):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # this is an include - apply to all nested patterns
                process_patterns(pattern.url_patterns)
            else:
                # this is a pattern
                pattern.callback = decorator(pattern.callback)

    process_patterns(url_list)
    return url_list, app_name, namespace


def main_character_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if user_has_main_character(request.user):
            return view_func(request, *args, **kwargs)

        messages.error(request, _('A main character is required to perform that action. Add one below.'))
        return redirect('authentication:dashboard')
    return login_required(_wrapped_view)
