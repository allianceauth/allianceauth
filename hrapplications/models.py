from django.db import models
from django.contrib.auth.models import User

from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo


class HRApplication(models.Model):
    character_name = models.CharField(max_length=254, default="")
    is_a_spi = models.CharField(max_length=254, default="")
    about = models.TextField(default="")
    extra = models.TextField(default="")

    corp = models.ForeignKey(EveCorporationInfo)
    user = models.ForeignKey(User)

    approved_denied = models.NullBooleanField(blank=True, null=True)
    reviewer_user = models.ForeignKey(User, blank=True, null=True, related_name="review_user")
    reviewer_character = models.ForeignKey(EveCharacter, blank=True, null=True)
    reviewer_inprogress_character = models.ForeignKey(EveCharacter, blank=True, null=True,
                                                      related_name="inprogress_character")

    def __str__(self):
        return self.character_name + " - Application"

    class Meta:
        permissions = (('approve_hrapplication', 'Can approve applications'), ('reject_hrapplication', 'Can reject applications'))


class HRApplicationComment(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    comment = models.CharField(max_length=254, default="")
    application = models.ForeignKey(HRApplication)
    commenter_user = models.ForeignKey(User)
    commenter_character = models.ForeignKey(EveCharacter)

    def __str__(self):
        return str(self.application.character_name) + " - Comment"
