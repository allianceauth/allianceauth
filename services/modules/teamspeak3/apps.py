from __future__ import unicode_literals

from django.apps import AppConfig


class Teamspeak3ServiceConfig(AppConfig):
    name = 'teamspeak3'

    def ready(self):
        from . import signals
