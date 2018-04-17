import logging
from django.db import models, transaction
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.authentication.models import State
from allianceauth.eveonline.models import EveCorporationInfo, EveAllianceInfo

logger = logging.getLogger(__name__)


def get_users_for_state(state: State):
    return User.objects.select_related('profile').prefetch_related('profile__main_character')\
            .filter(profile__state_id=state.pk)


class AutogroupsConfigManager(models.Manager):
    def update_groups_for_state(self, state: State):
        """
        Update all the Group memberships for the users
        who have State
        :param state: State to update for
        :return:
        """
        users = get_users_for_state(state)
        for config in self.filter(states=state):
            logger.debug("in state loop")
            for user in users:
                logger.debug("in user loop for {}".format(user))
                config.update_group_membership_for_user(user)

    def update_groups_for_user(self, user: User, state: State = None):
        """
        Update the Group memberships for the given users state
        :param user: User to update for
        :param state: State to update user for
        :return:
        """
        if state is None:
            state = user.profile.state
        for config in self.filter(states=state):
            # grant user new groups for their state
            config.update_group_membership_for_user(user)
        for config in self.exclude(states=state):
            # ensure user does not have groups from previous state
            config.remove_user_from_alliance_groups(user)
            config.remove_user_from_corp_groups(user)


class AutogroupsConfig(models.Model):
    OPT_TICKER = 'ticker'
    OPT_NAME = 'name'
    NAME_OPTIONS = (
        (OPT_TICKER, 'Ticker'),
        (OPT_NAME, 'Full name'),
    )

    states = models.ManyToManyField(State, related_name='autogroups')

    corp_groups = models.BooleanField(default=False,
                                      help_text="Setting this to false will delete all the created groups.")
    corp_group_prefix = models.CharField(max_length=50, default='Corp ', blank=True)
    corp_name_source = models.CharField(max_length=20, choices=NAME_OPTIONS, default=OPT_NAME)

    alliance_groups = models.BooleanField(default=False,
                                          help_text="Setting this to false will delete all the created groups.")
    alliance_group_prefix = models.CharField(max_length=50, default='Alliance ', blank=True)
    alliance_name_source = models.CharField(max_length=20, choices=NAME_OPTIONS, default=OPT_NAME)

    corp_managed_groups = models.ManyToManyField(
        Group, through='ManagedCorpGroup', related_name='corp_managed_config',
        help_text='A list of corporation groups created and maintained by this AutogroupConfig. '
                  'You should not edit this list unless you know what you\'re doing.')

    alliance_managed_groups = models.ManyToManyField(
        Group, through='ManagedAllianceGroup', related_name='alliance_managed_config',
        help_text='A list of alliance groups created and maintained by this AutogroupConfig. '
                  'You should not edit this list unless you know what you\'re doing.')

    replace_spaces = models.BooleanField(default=False)
    replace_spaces_with = models.CharField(
        max_length=10, default='', blank=True,
        help_text='Any spaces in the group name will be replaced with this.')

    objects = AutogroupsConfigManager()

    def __init__(self, *args, **kwargs):
        super(AutogroupsConfig, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return 'States: ' + (' '.join(list(self.states.all().values_list('name', flat=True))) if self.pk else str(None))

    def update_all_states_group_membership(self):
        list(map(self.update_group_membership_for_state, self.states.all()))

    def update_group_membership_for_state(self, state: State):
        list(map(self.update_group_membership_for_user, get_users_for_state(state)))

    @transaction.atomic
    def update_group_membership_for_user(self, user: User):
        self.update_alliance_group_membership(user)
        self.update_corp_group_membership(user)

    def user_entitled_to_groups(self, user: User) -> bool:
        try:
            return user.profile.state in self.states.all()
        except ObjectDoesNotExist:
            return False

    @transaction.atomic
    def update_alliance_group_membership(self, user: User):
        group = None
        try:
            if not self.alliance_groups or not self.user_entitled_to_groups(user):
                logger.debug('User {} does not have required state for alliance group membership'.format(user))
                return
            else:
                alliance = user.profile.main_character.alliance
                if alliance is None:
                    logger.debug('User {} alliance is None, cannot update group membership'.format(user))
                    return
                group = self.get_alliance_group(alliance)
        except EveAllianceInfo.DoesNotExist:
            logger.debug('User {} main characters alliance does not exist in the database. Creating.'.format(user))
            alliance = EveAllianceInfo.objects.create_alliance(user.profile.main_character.alliance_id)
            group = self.get_alliance_group(alliance)
        except AttributeError:
            logger.warning('User {} does not have a main character. Group membership not updated'.format(user))
        finally:
            self.remove_user_from_alliance_groups(user, except_group=group)
            if group is not None:
                logger.debug('Adding user {} to alliance group {}'.format(user, group))
                user.groups.add(group)

    @transaction.atomic
    def update_corp_group_membership(self, user: User):
        group = None
        try:
            if not self.corp_groups or not self.user_entitled_to_groups(user):
                logger.debug('User {} does not have required state for corp group membership'.format(user))
            else:
                corp = user.profile.main_character.corporation
                group = self.get_corp_group(corp)
        except EveCorporationInfo.DoesNotExist:
            logger.debug('User {} main characters corporation does not exist in the database. Creating.'.format(user))
            corp = EveCorporationInfo.objects.create_corporation(user.profile.main_character.corporation_id)
            group = self.get_corp_group(corp)
        except AttributeError:
            logger.warning('User {} does not have a main character. Group membership not updated'.format(user))
        finally:
            self.remove_user_from_corp_groups(user, except_group=group)
            if group is not None:
                logger.debug('Adding user {} to corp group {}'.format(user, group))
                user.groups.add(group)

    @transaction.atomic
    def remove_user_from_alliance_groups(self, user: User, except_group: Group = None):
        remove_groups = user.groups.filter(pk__in=self.alliance_managed_groups.all().values_list('pk', flat=True))
        if except_group is not None:
            remove_groups = remove_groups.exclude(pk=except_group.pk)
        list(map(user.groups.remove, remove_groups))

    @transaction.atomic
    def remove_user_from_corp_groups(self, user: User, except_group: Group = None):
        remove_groups = user.groups.filter(pk__in=self.corp_managed_groups.all().values_list('pk', flat=True))
        if except_group is not None:
            remove_groups = remove_groups.exclude(pk=except_group.pk)
        list(map(user.groups.remove, remove_groups))

    def get_alliance_group(self, alliance: EveAllianceInfo) -> Group:
        return self.create_alliance_group(alliance)

    def get_corp_group(self, corp: EveCorporationInfo) -> Group:
        return self.create_corp_group(corp)

    @transaction.atomic
    def create_alliance_group(self, alliance: EveAllianceInfo) -> Group:
        group, created = Group.objects.get_or_create(name=self.get_alliance_group_name(alliance))
        if created:
            ManagedAllianceGroup.objects.create(group=group, config=self, alliance=alliance)
        return group

    @transaction.atomic
    def create_corp_group(self, corp: EveCorporationInfo) -> Group:
        group, created = Group.objects.get_or_create(name=self.get_corp_group_name(corp))
        if created:
            ManagedCorpGroup.objects.create(group=group, config=self, corp=corp)
        return group

    def delete_alliance_managed_groups(self):
        """
        Deletes ALL managed alliance groups
        """
        for g in self.alliance_managed_groups.all():
            g.delete()

    def delete_corp_managed_groups(self):
        """
        Deletes ALL managed corp groups
        """
        for g in self.corp_managed_groups.all():
            g.delete()

    def get_alliance_group_name(self, alliance: EveAllianceInfo) -> str:
        if self.alliance_name_source == self.OPT_TICKER:
            name = alliance.alliance_ticker
        elif self.alliance_name_source == self.OPT_NAME:
            name = alliance.alliance_name
        else:
            raise NameSourceException('Not a valid name source')
        return self._replace_spaces(self.alliance_group_prefix + name)

    def get_corp_group_name(self, corp: EveCorporationInfo) -> str:
        if self.corp_name_source == self.OPT_TICKER:
            name = corp.corporation_ticker
        elif self.corp_name_source == self.OPT_NAME:
            name = corp.corporation_name
        else:
            raise NameSourceException('Not a valid name source')
        return self._replace_spaces(self.corp_group_prefix + name)

    def _replace_spaces(self, name: str) -> str:
        """
        Replace the spaces in the given name based on the config
        :param name: name to replace spaces in
        :return: name with spaces replaced with the configured character(s) or unchanged if configured
        """
        if self.replace_spaces:
            return name.strip().replace(' ', str(self.replace_spaces_with))
        return name


class ManagedGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    config = models.ForeignKey(AutogroupsConfig, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ManagedCorpGroup(ManagedGroup):
    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE)


class ManagedAllianceGroup(ManagedGroup):
    alliance = models.ForeignKey(EveAllianceInfo, on_delete=models.CASCADE)


class NameSourceException(Exception):
    pass
