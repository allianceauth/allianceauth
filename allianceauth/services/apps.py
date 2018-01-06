from django.apps import AppConfig


class ServicesConfig(AppConfig):
    name = 'allianceauth.services'
    label = 'services'

    def ready(self):
        from . import signals
