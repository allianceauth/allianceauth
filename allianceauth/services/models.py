from django.db import models

from allianceauth.authentication.models import State


class NameFormatConfig(models.Model):
    service_name = models.CharField(max_length=100, blank=False, null=False)
    default_to_username = models.BooleanField(default=True, help_text="If a user has no main_character, "
                                                                      "default to using their Auth username instead.")
    format = models.CharField(max_length=100, blank=False, null=False,
                              help_text='For information on constructing name formats, please see the '
                                        '<a href="https://allianceauth.readthedocs.io/en/latest/features/nameformats">'
                                        'name format documentation</a>')
    states = models.ManyToManyField(State, help_text="States to apply this format to. You should only have one "
                                                     "formatter for each state for each service.")


