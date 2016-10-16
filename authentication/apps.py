from __future__ import unicode_literals

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = 'authentication'

    def ready(self):
        import authentication.signals
