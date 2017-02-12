from __future__ import unicode_literals
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from authentication.models import AuthServicesInfo
from authentication.states import MEMBER_STATE, BLUE_STATE
from authentication.tasks import make_member, make_blue, disable_member
from services.tasks import validate_services
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=AuthServicesInfo)
def pre_save_auth_state(sender, instance, *args, **kwargs):
    if instance.pk:
        old_instance = AuthServicesInfo.objects.get(pk=instance.pk)
        if old_instance.state != instance.state:
            logger.debug('Detected state change for %s' % instance.user)
            if instance.state == MEMBER_STATE:
                make_member(instance)
            elif instance.state == BLUE_STATE:
                make_blue(instance)
            else:
                disable_member(instance.user)
            validate_services.apply(args=(instance.user,))


@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, *args, **kwargs):
    # ensure all users have a model
    if created:
        AuthServicesInfo.objects.get_or_create(user=instance)

