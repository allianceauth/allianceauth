import logging

from django.db import transaction
from django.db.models import Manager, QuerySet, Q

from allianceauth.eveonline.models import EveCharacter

logger = logging.getLogger(__name__)


def available_states_query(character):
    query = Q(public=True)
    if character.character_id:
        query |= Q(member_characters__character_id=character.character_id)
    if character.corporation_id:
        query |= Q(member_corporations__corporation_id=character.corporation_id)
    if character.alliance_id:
        query |= Q(member_alliances__alliance_id=character.alliance_id)
    return query


class CharacterOwnershipManager(Manager):
    def create_by_token(self, token):
        if not EveCharacter.objects.filter(character_id=token.character_id).exists():
            EveCharacter.objects.create_character(token.character_id)
        return self.create(character=EveCharacter.objects.get(character_id=token.character_id), user=token.user,
                           owner_hash=token.character_owner_hash)


class StateQuerySet(QuerySet):
    def available_to_character(self, character):
        return self.filter(available_states_query(character))

    def available_to_user(self, user):
        if user.profile.main_character:
            return self.available_to_character(user.profile.main_character)
        else:
            return self.none()

    def get_for_user(self, user):
        states = self.available_to_user(user)
        if states.exists():
            return states[0]
        else:
            from allianceauth.authentication.models import get_guest_state
            return get_guest_state()

    def delete(self):
        with transaction.atomic():
            for state in self:
                for profile in state.userprofile_set.all():
                    profile.assign_state(state=self.model.objects.exclude(pk=state.pk).get_for_user(profile.user))
        super(StateQuerySet, self).delete()


class StateManager(Manager):
    def get_queryset(self):
        return StateQuerySet(self.model, using=self._db)

    def available_to_character(self, character):
        return self.get_queryset().available_to_character(character)

    def available_to_user(self, user):
        return self.get_queryset().available_to_user(user)

    def get_for_character(self, character):
        states = self.get_queryset().available_to_character(character)
        if states.exists():
            return states[0]
        else:
            from allianceauth.authentication.models import get_guest_state
            return get_guest_state()

    def get_for_user(self, user):
        return self.get_queryset().get_for_user(user)
