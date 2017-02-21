from django.utils.encoding import python_2_unicode_compatible
from esi.clients import esi_client_factory
from django.conf import settings
from django.core.cache import cache
import json
from bravado.exception import HTTPNotFound, HTTPUnprocessableEntity
import evelink
import logging

logger = logging.getLogger(__name__)

# optional setting to control cached object lifespan
OBJ_CACHE_DURATION = int(getattr(settings, 'EVEONLINE_OBJ_CACHE_DURATION', 300))


@python_2_unicode_compatible
class ObjectNotFound(Exception):
    def __init__(self, obj_id, type_name):
        self.id = obj_id
        self.type = type_name

    def __str__(self):
        return '%s with ID %s not found.' % (self.type, self.id)


@python_2_unicode_compatible
class Entity(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{} ({}): {}>".format(self.__class__.__name__, self.id, self.name)

    def __bool__(self):
        return bool(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict['id'], data_dict['name'])


class Corporation(Entity):
    def __init__(self, provider, id, name, ticker, ceo_id, members, alliance_id):
        super(Corporation, self).__init__(id, name)
        self.provider = provider
        self.ticker = ticker
        self.ceo_id = ceo_id
        self.members = members
        self.alliance_id = alliance_id
        self._alliance = None
        self._ceo = None

    @property
    def alliance(self):
        if self.alliance_id:
            if not self._alliance:
                self._alliance = self.provider.get_alliance(self.alliance_id)
            return self._alliance
        return Entity(None, None)

    @property
    def ceo(self):
        if not self._ceo:
            self._ceo = self.provider.get_character(self.ceo_id)
        return self._ceo

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'ticker': self.ticker,
            'ceo_id': self.ceo_id,
            'members': self.members,
            'alliance_id': self.alliance_id
        }

    @classmethod
    def from_dict(cls, dict):
        return cls(
            None,
            dict['id'],
            dict['name'],
            dict['ticker'],
            dict['ceo_id'],
            dict['members'],
            dict['alliance_id'],
        )


class Alliance(Entity):
    def __init__(self, provider, id, name, ticker, corp_ids, executor_corp_id):
        super(Alliance, self).__init__(id, name)
        self.provider = provider
        self.ticker = ticker
        self.corp_ids = corp_ids
        self.executor_corp_id = executor_corp_id
        self._corps = {}

    def corp(self, id):
        assert id in self.corp_ids
        if id not in self._corps:
            self._corps[id] = self.provider.get_corp(id)
            self._corps[id]._alliance = self
        return self._corps[id]

    @property
    def corps(self):
        return sorted([self.corp(id) for id in self.corp_ids], key=lambda x: x.name)

    @property
    def executor_corp(self):
        return self.corp(self.executor_corp_id)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'ticker': self.ticker,
            'corp_ids': self.corp_ids,
            'executor_corp_id': self.executor_corp_id,
        }

    @classmethod
    def from_dict(cls, dict):
        return cls(
            None,
            dict['id'],
            dict['name'],
            dict['ticker'],
            dict['corp_ids'],
            dict['executor_corp_id'],
        )


class Character(Entity):
    def __init__(self, provider, id, name, corp_id, alliance_id):
        super(Character, self).__init__(id, name)
        self.provider = provider
        self.corp_id = corp_id
        self.alliance_id = alliance_id
        self._corp = None
        self._alliance = None

    @property
    def corp(self):
        if not self._corp:
            self._corp = self.provider.get_corp(self.corp_id)
        return self._corp

    @property
    def alliance(self):
        if self.alliance_id:
            return self.corp.alliance
        return Entity(None, None)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'corp_id': self.corp_id,
            'alliance_id': self.alliance_id,
        }

    @classmethod
    def from_dict(cls, dict):
        return cls(
            None,
            dict['id'],
            dict['name'],
            dict['corp_id'],
            dict['alliance_id'],
        )


class ItemType(Entity):
    def __init__(self, provider, type_id, name):
        super(ItemType, self).__init__(type_id, name)
        self.provider = provider

    @classmethod
    def from_dict(cls, data_dict):
        return cls(
            None,
            data_dict['id'],
            data_dict['name'],
        )


class EveProvider(object):
    def get_alliance(self, alliance_id):
        """
        :return: an Alliance object for the given ID
        """
        raise NotImplementedError()

    def get_corp(self, corp_id):
        """
        :return: a Corporation object for the given ID
        """
        raise NotImplementedError()

    def get_character(self, character_id):
        """
        :return: a Character object for the given ID
        """
        raise NotImplementedError()

    def get_itemtype(self, type_id):
        """
        :return: an ItemType object for the given ID
        """
        raise NotImplemented()


@python_2_unicode_compatible
class EveSwaggerProvider(EveProvider):
    def __init__(self, token=None, adapter=None):
        self.client = esi_client_factory(token=token, Alliance='v1', Character='v4', Corporation='v2', Universe='v2')
        self.adapter = adapter or self

    def __str__(self):
        return 'esi'

    def get_alliance(self, alliance_id):
        try:
            data = self.client.Alliance.get_alliances_alliance_id(alliance_id=alliance_id).result()
            corps = self.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance_id).result()
            model = Alliance(
                self.adapter,
                alliance_id,
                data['alliance_name'],
                data['ticker'],
                corps,
                data['executor_corporation_id'],
            )
            return model
        except HTTPNotFound:
            raise ObjectNotFound(alliance_id, 'alliance')

    def get_corp(self, corp_id):
        try:
            data = self.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).result()
            model = Corporation(
                self.adapter,
                corp_id,
                data['corporation_name'],
                data['ticker'],
                data['ceo_id'],
                data['member_count'],
                data['alliance_id'] if 'alliance_id' in data else None,
            )
            return model
        except HTTPNotFound:
            raise ObjectNotFound(id, 'corporation')

    def get_character(self, character_id):
        try:
            data = self.client.Character.get_characters_character_id(character_id=character_id).result()
            alliance_id = self.adapter.get_corp(data['corporation_id']).alliance_id
            model = Character(
                self.adapter,
                character_id,
                data['name'],
                data['corporation_id'],
                alliance_id,
            )
            return model
        except (HTTPNotFound, HTTPUnprocessableEntity):
            raise ObjectNotFound(character_id, 'character')

    def get_itemtype(self, type_id):
        try:
            data = self.client.Universe.get_universe_types_type_id(type_id=type_id).result()
            return ItemType(self.adapter, type_id, data['name'])
        except (HTTPNotFound, HTTPUnprocessableEntity):
            raise ObjectNotFound(type_id, 'type')


@python_2_unicode_compatible
class EveXmlProvider(EveProvider):
    def __init__(self, api_key=None, adapter=None):
        """
        :param api_key: eveonline.EveApiKeyPair
        """
        self.api = evelink.api.API(api_key=(api_key.api_id, api_key.api_key)) if api_key else evelink.api.API()
        self.adapter = adapter or self

    def __str__(self):
        return 'xml'

    def get_alliance(self, id):
        api = evelink.eve.EVE(api=self.api)
        alliances = api.alliances().result
        try:
            results = alliances[int(id)]
        except KeyError:
            raise ObjectNotFound(id, 'alliance')
        model = Alliance(
            self.adapter,
            id,
            results['name'],
            results['ticker'],
            results['member_corps'],
            results['executor_id'],
        )
        return model

    def get_corp(self, id):
        api = evelink.corp.Corp(api=self.api)
        try:
            corpinfo = api.corporation_sheet(corp_id=int(id)).result
        except evelink.api.APIError as e:
            if int(e.code) == 523:
                raise ObjectNotFound(id, 'corporation')
            raise e
        model = Corporation(
            self.adapter,
            id,
            corpinfo['name'],
            corpinfo['ceo']['id'],
            corpinfo['members']['current'],
            corpinfo['ticker'],
            corpinfo['alliance']['id'] if corpinfo['alliance'] else None,
        )
        return model

    def _build_character(self, result):
        return Character(
            self.adapter,
            result['id'],
            result['name'],
            result['corp']['id'],
            result['alliance']['id'],
        )

    def get_character(self, id):
        api = evelink.eve.EVE(api=self.api)
        try:
            charinfo = api.character_info_from_id(id).result
        except evelink.api.APIError as e:
            if int(e.code) == 105:
                raise ObjectNotFound(id, 'character')
            raise e
        return self._build_character(charinfo)

    def get_itemtype(self, type_id):
        api = evelink.eve.EVE(api=self.api)
        try:
            type_name = api.type_name_from_id(type_id).result
            assert type_name != 'Unknown Type'
            return ItemType(self.adapter, type_id, type_name)
        except AssertionError:
            raise ObjectNotFound(type_id, 'itemtype')


class EveAdapter(EveProvider):
    """
    Redirects queries to appropriate data source.
    """

    def __init__(self, char_provider, corp_provider, alliance_provider, itemtype_provider):
        self.char_provider = char_provider
        self.corp_provider = corp_provider
        self.alliance_provider = alliance_provider
        self.itemtype_provider = itemtype_provider
        self.char_provider.adapter = self
        self.corp_provider.adapter = self
        self.alliance_provider.adapter = self
        self.itemtype_provider.adapter = self

    def __repr__(self):
        return "<{} (character:{} corp:{} alliance:{} itemtype:{})>".format(self.__class__.__name__,
                                                                            str(self.char_provider),
                                                                            str(self.corp_provider),
                                                                            str(self.alliance_provider),
                                                                            str(self.itemtype_provider))

    @staticmethod
    def _get_from_cache(obj_class, id):
        data = cache.get('%s__%s' % (obj_class.__name__.lower(), id))
        if data:
            obj = obj_class.from_dict(json.loads(data))
            logger.debug('Got from cache: %s' % obj.__repr__())
            return obj
        else:
            return None

    @staticmethod
    def _cache(obj):
        logger.debug('Caching: %s ' % obj.__repr__())
        cache.set('%s__%s' % (obj.__class__.__name__.lower(), obj.id), json.dumps(obj.serialize()),
                  int(OBJ_CACHE_DURATION))

    def get_character(self, id):
        obj = self._get_from_cache(Character, id)
        if obj:
            obj.provider = self
        else:
            obj = self._get_character(id)
            self._cache(obj)
        return obj

    def get_corp(self, id):
        obj = self._get_from_cache(Corporation, id)
        if obj:
            obj.provider = self
        else:
            obj = self._get_corp(id)
            self._cache(obj)
        return obj

    def get_alliance(self, id):
        obj = self._get_from_cache(Alliance, id)
        if obj:
            obj.provider = self
        else:
            obj = self._get_alliance(id)
            self._cache(obj)
        return obj

    def get_itemtype(self, type_id):
        obj = self._get_from_cache(ItemType, type_id)
        if obj:
            obj.provider = self
        else:
            obj = self._get_itemtype(type_id)
            self._cache(obj)
        return obj

    def _get_character(self, id):
        return self.char_provider.get_character(id)

    def _get_corp(self, id):
        return self.corp_provider.get_corp(id)

    def _get_alliance(self, id):
        return self.alliance_provider.get_alliance(id)

    def _get_itemtype(self, type_id):
        return self.itemtype_provider.get_itemtype(type_id)


CHARACTER_PROVIDER = getattr(settings, 'EVEONLINE_CHARACTER_PROVIDER', '') or 'esi'
CORP_PROVIDER = getattr(settings, 'EVEONLINE_CORP_PROVIDER', '') or 'esi'
ALLIANCE_PROVIDER = getattr(settings, 'EVEONLINE_ALLIANCE_PROVIDER', '') or 'esi'
ITEMTYPE_PROVIDER = getattr(settings, 'EVEONLINE_ITEMTYPE_PROVIDER', '') or 'esi'


def eve_adapter_factory(character_source=CHARACTER_PROVIDER, corp_source=CORP_PROVIDER,
                        alliance_source=ALLIANCE_PROVIDER, itemtype_source=ITEMTYPE_PROVIDER, api_key=None, token=None):
    sources = [character_source, corp_source, alliance_source, itemtype_source]
    providers = []

    if 'xml' in sources:
        xml = EveXmlProvider(api_key=api_key)
    if 'esi' in sources:
        esi = EveSwaggerProvider(token=token)

    for source in sources:
        if source == 'xml':
            providers.append(xml)
        elif source == 'esi':
            providers.append(esi)
        else:
            raise ValueError('Unrecognized data source "%s"' % source)
    return EveAdapter(providers[0], providers[1], providers[2], providers[3])
