from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from eveonline.models import EveCorporationInfo, EveCharacter
from esi.models import Token
from esi.errors import TokenError
from notifications import notify
from authentication.models import CharacterOwnership, UserProfile
from bravado.exception import HTTPForbidden
from corputils.managers import CorpStatsManager
from operator import attrgetter
import json
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class CorpStats(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    corp = models.OneToOneField(EveCorporationInfo)
    last_update = models.DateTimeField(auto_now=True)
    _members = models.TextField(default='{}')

    class Meta:
        permissions = (
            ('corp_apis', 'Can view API keys of members of their corporation.'),
            ('alliance_apis', 'Can view API keys of members of their alliance.'),
            ('blue_apis', 'Can view API keys of members of blue corporations.'),
            ('view_corp_corpstats', 'Can view corp stats of their corporation.'),
            ('view_alliance_corpstats', 'Can view corp stats of members of their alliance.'),
            ('view_blue_corpstats', 'Can view corp stats of blue corporations.'),
        )
        verbose_name = "corp stats"
        verbose_name_plural = "corp stats"

    objects = CorpStatsManager()

    def __str__(self):
        return "%s for %s" % (self.__class__.__name__, self.corp)

    def update(self):
        try:
            c = self.token.get_esi_client(Character='v4', Corporation='v2')
            assert c.Character.get_characters_character_id(character_id=self.token.character_id).result()[
                       'corporation_id'] == int(self.corp.corporation_id)
            members = c.Corporation.get_corporations_corporation_id_members(
                corporation_id=self.corp.corporation_id).result()
            member_ids = [m['character_id'] for m in members]

            # requesting too many ids per call results in a HTTP400
            # the swagger spec doesn't have a maxItems count
            # manual testing says we can do over 350, but let's not risk it
            member_id_chunks = [member_ids[i:i + 255] for i in range(0, len(member_ids), 255)]
            c = self.token.get_esi_client(Character='v1') # ccplease bump versions of whole resources
            member_name_chunks = [c.Character.get_characters_names(character_ids=id_chunk).result() for id_chunk in
                                  member_id_chunks]
            member_list = {}
            for name_chunk in member_name_chunks:
                member_list.update({m['character_id']: m['character_name'] for m in name_chunk})

            self.members = member_list
            self.save()
        except TokenError as e:
            logger.warning("%s failed to update: %s" % (self, e))
            if self.token.user:
                notify(self.token.user, "%s failed to update with your ESI token." % self,
                       message="Your token has expired or is no longer valid. Please add a new one to create a new CorpStats.",
                       level="error")
            self.delete()
        except HTTPForbidden as e:
            logger.warning("%s failed to update: %s" % (self, e))
            if self.token.user:
                notify(self.token.user, "%s failed to update with your ESI token." % self,
                       message="%s: %s" % (e.status_code, e.message), level="error")
            self.delete()
        except AssertionError:
            logger.warning("%s token character no longer in corp." % self)
            if self.token.user:
                notify(self.token.user, "%s cannot update with your ESI token." % self,
                       message="%s cannot update with your ESI token as you have left corp." % self, level="error")
            self.delete()

    @property
    def members(self):
        return json.loads(self._members)

    @members.setter
    def members(self, dict):
        self._members = json.dumps(dict)

    @property
    def member_ids(self):
        return [id for id, name in self.members.items()]

    @property
    def member_names(self):
        return [name for id, name in self.members.items()]

    def member_count(self):
        return len(self.members)

    @staticmethod
    def user_count(members):
        mainchars = []
        for member in members:
            if hasattr(member.main, 'character_name'):
                mainchars.append(member.main.character_name)
        return len(set(mainchars))

    def registered_characters(self):
        return len(CharacterOwnership.objects.filter(character__character_id__in=self.member_ids))

    @python_2_unicode_compatible
    class MemberObject(object):
        def __init__(self, character_id, character_name):
            self.character_id = character_id
            self.character_name = character_name
            try:
                char = EveCharacter.objects.get(character_id=character_id)
                self.main_user = char.character_ownership.user
                self.main = self.main_user.profile.main_character
                self.registered = True
            except (EveCharacter.DoesNotExist, CharacterOwnership.DoesNotExist, UserProfile.DoesNotExist, AttributeError):
                self.main = None
                self.registered = False
                self.main_user = ''

        def __str__(self):
            return self.character_name

        def portrait_url(self, size=32):
            return "https://image.eveonline.com/Character/%s_%s.jpg" % (self.character_id, size)

    def get_member_objects(self):
        member_list = [CorpStats.MemberObject(id, name) for id, name in self.members.items()]
        outlist = sorted([m for m in member_list if m.main_user], key=attrgetter('main_user', 'character_name'))
        outlist = outlist + sorted([m for m in member_list if not m.main_user], key=attrgetter('character_name'))
        return outlist

    def can_update(self, user):
        return user.is_superuser or user == self.token.user

    @python_2_unicode_compatible
    class ViewModel(object):
        def __init__(self, corpstats, user):
            self.corp = corpstats.corp
            self.members = corpstats.get_member_objects(user)
            self.can_update = corpstats.can_update(user)
            self.total_members = len(self.members)
            self.total_users = corpstats.user_count(self.members)
            self.registered_members = corpstats.registered_characters()
            self.last_updated = corpstats.last_update

        def __str__(self):
            return str(self.corp)

        def corp_logo(self, size=128):
            return "https://image.eveonline.com/Corporation/%s_%s.png" % (self.corp.corporation_id, size)

        def alliance_logo(self, size=128):
            if self.corp.alliance:
                return "https://image.eveonline.com/Alliance/%s_%s.png" % (self.corp.alliance.alliance_id, size)
            else:
                return "https://image.eveonline.com/Alliance/1_%s.png" % size

    def get_view_model(self, user):
        return CorpStats.ViewModel(self, user)
