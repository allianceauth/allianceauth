from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.checks import register, Tags


class AuthenticationConfig(AppConfig):
    name = 'authentication'

    def ready(self):
        super(AuthenticationConfig, self).ready()
        import authentication.signals
        from authentication import checks
        register(Tags.security)(checks.check_login_scopes_setting)
