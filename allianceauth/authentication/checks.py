from django.core.checks import Error
from django.conf import settings


def check_login_scopes_setting(*args, **kwargs):
    errors = []
    try:
        assert settings.LOGIN_TOKEN_SCOPES
    except (AssertionError, AttributeError):
        errors.append(Error('LOGIN_TOKEN_SCOPES setting cannot be blank.',
                            hint='SSO tokens used for logging in must require scopes to be refreshable.'))
    return errors
