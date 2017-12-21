from django.apps import AppConfig


class EveAutogroupsConfig(AppConfig):
    name = 'allianceauth.eveonline.autogroups'
    label = 'eve_autogroups'

    def ready(self):
        import allianceauth.eveonline.autogroups.signals
