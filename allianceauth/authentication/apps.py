from django.apps import AppConfig
from django.core.checks import register, Tags


class AuthenticationConfig(AppConfig):
    name = 'allianceauth.authentication'
    label = 'authentication'

    def ready(self):
        super(AuthenticationConfig, self).ready()
        from allianceauth.authentication import checks, signals
        register(Tags.security)(checks.check_login_scopes_setting)
