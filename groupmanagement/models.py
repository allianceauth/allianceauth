from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from eveonline.models import EveCharacter


@python_2_unicode_compatible
class GroupRequest(models.Model):
    status = models.CharField(max_length=254)
    leave_request = models.BooleanField(default=0)
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    main_char = models.ForeignKey(EveCharacter)

    def __str__(self):
        return self.user.username + ":" + self.group.name


@python_2_unicode_compatible
class AuthGroup(models.Model):
    """
    Extends Django Group model with a one-to-one field
    Attributes are accessible via group as if they were in the model
    e.g. group.authgroup.internal

    Logic:
    Internal - not requestable by users, at all. Covers Corp_, Alliance_, Members etc groups.
    Groups are internal by default

    Public - Other options are respected, but any user will be able to become and remain a member, even if they
    have no API etc entered. Auth will not manage these groups automatically so user removal is up to
    group managers/leaders.

    Not Internal and:
        Hidden - users cannot view, can request if they have the direct link.
        Not Hidden - Users can view and request the group
        Open - Users are automatically accepted into the group
        Not Open - Users requests must be approved before they are added to the group
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE, primary_key=True)

    internal = models.BooleanField(default=True,
                                   help_text="Internal group, users cannot see, join or request to join this group.<br>"
                                             "Used for groups such as Members, Corp_*, Alliance_* etc.<br>"
                                             "<b>Overrides Hidden and Open options when selected.</b>")
    hidden = models.BooleanField(default=True,
                                 help_text="Group is hidden from users but can still join with the correct link.")
    open = models.BooleanField(default=False,
                               help_text="Group is open and users will be automatically added upon request. <br>"
                                         "If the group is not open users will need their request manually approved.")
    public = models.BooleanField(default=False,
                                 help_text="Group is public. Any registered user is able to join this group, with "
                                           "visibility based on the other options set for this group.<br> Auth will "
                                           "not remove users from this group automatically when they are no longer "
                                           "authenticated.")
    # Group leaders have management access to this group
    group_leaders = models.ManyToManyField(User, related_name='leads_groups', blank=True,
                                           help_text="Group leaders can process group requests for this group "
                                                     "specifically. Use the auth.group_management permission to allow "
                                                     "a user to manage all groups.")

    description = models.CharField(max_length=512, blank=True, help_text="Description of the group shown to users.")

    def __str__(self):
        return self.group.name

    class Meta:
        permissions = (
            ("request_groups", u"Can request non-public groups"),
        )


@receiver(post_save, sender=Group)
def create_auth_group(sender, instance, created, **kwargs):
    """
    Creates the AuthGroup model when a group is created
    """
    if created:
        AuthGroup.objects.create(group=instance)


@receiver(post_save, sender=Group)
def save_auth_group(sender, instance, **kwargs):
    """
    Ensures AuthGroup model is saved automatically
    """
    instance.authgroup.save()
