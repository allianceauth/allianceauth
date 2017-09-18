from django.apps import AppConfig


class Teamspeak3ServiceConfig(AppConfig):
    name = 'allianceauth.services.modules.teamspeak3'
    label = 'teamspeak3'

    def ready(self):
        from . import signals
