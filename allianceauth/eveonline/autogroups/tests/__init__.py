from unittest import mock
from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from allianceauth.authentication.models import UserProfile
from allianceauth.authentication.signals import reassess_on_profile_save
from .. import signals
from ..models import AutogroupsConfig

MODULE_PATH = 'allianceauth.eveonline.autogroups'


def patch(target, *args, **kwargs):
    return mock.patch('{}{}'.format(MODULE_PATH, target), *args, **kwargs)


def connect_signals():
    post_save.connect(receiver=reassess_on_profile_save, sender=UserProfile)
    pre_save.connect(receiver=signals.pre_save_config, sender=AutogroupsConfig)
    pre_delete.connect(receiver=signals.pre_delete_config, sender=AutogroupsConfig)
    post_save.connect(receiver=signals.check_groups_on_profile_update, sender=UserProfile)
    m2m_changed.connect(receiver=signals.autogroups_states_changed, sender=AutogroupsConfig.states.through)


def disconnect_signals():
    post_save.disconnect(receiver=reassess_on_profile_save, sender=UserProfile)
    pre_save.disconnect(receiver=signals.pre_save_config, sender=AutogroupsConfig)
    pre_delete.disconnect(receiver=signals.pre_delete_config, sender=AutogroupsConfig)
    post_save.disconnect(receiver=signals.check_groups_on_profile_update, sender=UserProfile)
    m2m_changed.disconnect(receiver=signals.autogroups_states_changed, sender=AutogroupsConfig.states.through)
