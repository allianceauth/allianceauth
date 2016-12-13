from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from eveonline.models import EveCorporationInfo, EveCharacter, EveApiKeyPair
from esi.models import Token
from esi.errors import TokenError
from notifications import notify
from authentication.models import AuthServicesInfo
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
        )
        default_permissions = (
            'add',
            'delete',
            'view',
        )
        verbose_name = "Corp stats"

    objects = CorpStatsManager()

    def __str__(self):
        return "%s for %s" % (self.__class__.__name__, self.corp)

    def update(self):
        try:
            c = self.token.get_esi_client()
            assert c.Character.get_characters_character_id(character_id=self.token.character_id).result()['corporation_id'] == int(self.corp.corporation_id)
            members = c.Corporation.get_corporations_corporation_id_members(corporation_id=self.corp.corporation_id).result()
            member_ids = [m['character_id'] for m in members]
            member_names = c.Character.get_characters_names(character_ids=member_ids).result()
            member_list = {m['character_id']:m['character_name'] for m in member_names}
            self.members = member_list
            self.save()
        except TokenError as e:
            logger.warning("%s failed to update: %s" % (self, e))
            if self.token.user:
                notify(self.token.user, "%s failed to update with your ESI token." % self, message="Your token has expired or is no longer valid. Please add a new one to create a new CorpStats.", level="error")
            self.delete()
        except HTTPForbidden as e:
            logger.warning("%s failed to update: %s" % (self, e))
            if self.token.user:
                notify(self.token.user, "%s failed to update with your ESI token." % self, message="%s: %s" % (e.status_code, e.message), level="error")
            self.delete()
        except AssertionError:
            logger.warning("%s token character no longer in corp." % self)
            if self.token.user:
                notify(self.token.user, "%s cannot update with your ESI token." % self, message="%s cannot update with your ESI token as you have left corp." % self, level="error")
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

    def show_apis(self, user):
        auth = AuthServicesInfo.objects.get_or_create(user=user)[0]
        if auth.main_char_id:
            try:
                char = EveCharacter.objects.get(id=auth.main_char_id)
                if char.corporation_id == self.corp.corporation_id and user.has_perm('corputils.corp_apis'):
                    return True
                elif char.alliance_id == self.corp.alliance_id and user.has_perm('corputils.alliance_apis'):
                    return True
                elif user.has_perm('corputils.blue_apis') and self.corp.is_blue:
                    return True
            except EveCharacter.DoesNotExist:
                pass
        return user.is_superuser

    def entered_apis(self):
        return EveCharacter.objects.filter(character_id__in=self.member_ids).exclude(api_id__isnull=True).count()

    def member_count(self):
        return len(self.members)


    @python_2_unicode_compatible
    class MemberObject(object):
        def __init__(self, character_id, character_name, show_apis=False):
            self.character_id = character_id
            self.character_name = character_name
            try:
                char = EveCharacter.objects.get(character_id=character_id)
                auth = AuthServicesInfo.objects.get(user=char.user)
                try:
                    self.main = EveCharacter.objects.get(character_id=auth.main_char_id)
                except EveCharacter.DoesNotExist:
                    self.main = None
                if show_apis:
                    self.api = EveApiKeyPair.objects.get(api_id=char.api_id)
            except (EveCharacter.DoesNotExist, AuthServicesInfo.DoesNotExist):
                self.main = None
                self.api = None
            except EveApiKeyPair.DoesNotExist:
                self.api = None

        def __str__(self):
            return self.character_name

        def portrait_url(self, size=32):
            return "https://image.eveonline.com/Character/%s_%s.jpg" % (self.character_id, size)

    def get_member_objects(self, user):
        show_apis = self.show_apis(user)
        return sorted([CorpStats.MemberObject(id, name, show_apis=show_apis) for id, name in self.members.items()], key=attrgetter('character_name'))

    def can_update(self, user):
        return user.is_superuser or user == self.token.user


    @python_2_unicode_compatible
    class ViewModel(object):
        def __init__(self, corpstats, user):
            self.corp = corpstats.corp
            self.members = corpstats.get_member_objects(user)
            self.can_update = corpstats.can_update(user)
            self.total_members = len(self.members)
            self.registered_members = corpstats.entered_apis()
            self.show_apis = corpstats.show_apis(user)
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
