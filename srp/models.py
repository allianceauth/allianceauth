from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.utils import timezone
from eveonline.models import EveCharacter


@python_2_unicode_compatible
class SrpFleetMain(models.Model):
    fleet_name = models.CharField(max_length=254, default="")
    fleet_doctrine = models.CharField(max_length=254, default="")
    fleet_time = models.DateTimeField()
    fleet_srp_code = models.CharField(max_length=254, default="")
    fleet_srp_status = models.CharField(max_length=254, default="")
    fleet_commander = models.ForeignKey(EveCharacter)
    fleet_srp_aar_link = models.CharField(max_length=254, default="")

    def __str__(self):
        return self.fleet_name + " - SrpFleetMain"


@python_2_unicode_compatible
class SrpUserRequest(models.Model):
    killboard_link = models.CharField(max_length=254, default="")
    after_action_report_link = models.CharField(max_length=254, default="")
    additional_info = models.CharField(max_length=254, default="")
    srp_status = models.CharField(max_length=254, default="")
    srp_total_amount = models.BigIntegerField(default=0)
    character = models.ForeignKey(EveCharacter)
    srp_fleet_main = models.ForeignKey(SrpFleetMain)
    kb_total_loss = models.BigIntegerField(default=0)
    srp_ship_name = models.CharField(max_length=254, default="")
    post_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.character.character_name + " - SrpUserRequest"
