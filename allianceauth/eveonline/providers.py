from esi.clients import esi_client_factory
from bravado.exception import HTTPNotFound, HTTPUnprocessableEntity
import logging
import os

SWAGGER_SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swagger.json')
"""
Swagger spec operations:

get_alliances_alliance_id
get_alliances_alliance_id_corporations
get_corporations_corporation_id
get_characters_character_id
get_universe_types_type_id
"""


logger = logging.getLogger(__name__)


class ObjectNotFound(Exception):
    def __init__(self, obj_id, type_name):
        self.id = obj_id
        self.type = type_name

    def __str__(self):
        return '%s with ID %s not found.' % (self.type, self.id)


class Entity(object):
    def __init__(self, id=None, name=None):
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


class Corporation(Entity):
    def __init__(self, ticker=None, ceo_id=None, members=None, alliance_id=None, **kwargs):
        super(Corporation, self).__init__(**kwargs)
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
                self._alliance = provider.get_alliance(self.alliance_id)
            return self._alliance
        return Entity(None, None)

    @property
    def ceo(self):
        if not self._ceo:
            self._ceo = provider.get_character(self.ceo_id)
        return self._ceo


class Alliance(Entity):
    def __init__(self, ticker=None, corp_ids=None, executor_corp_id=None, **kwargs):
        super(Alliance, self).__init__(**kwargs)
        self.ticker = ticker
        self.corp_ids = corp_ids
        self.executor_corp_id = executor_corp_id
        self._corps = {}

    def corp(self, id):
        assert id in self.corp_ids
        if id not in self._corps:
            self._corps[id] = provider.get_corp(id)
            self._corps[id]._alliance = self
        return self._corps[id]

    @property
    def corps(self):
        return sorted([self.corp(c_id) for c_id in self.corp_ids], key=lambda x: x.name)

    @property
    def executor_corp(self):
        if self.executor_corp_id:
            return self.corp(self.executor_corp_id)
        return Entity(None, None)


class Character(Entity):
    def __init__(self, corp_id=None, alliance_id=None, **kwargs):
        super(Character, self).__init__(**kwargs)
        self.corp_id = corp_id
        self.alliance_id = alliance_id
        self._corp = None
        self._alliance = None

    @property
    def corp(self):
        if not self._corp:
            self._corp = provider.get_corp(self.corp_id)
        return self._corp

    @property
    def alliance(self):
        if self.alliance_id:
            return self.corp.alliance
        return Entity(None, None)


class ItemType(Entity):
    def __init__(self, **kwargs):
        super(ItemType, self).__init__(**kwargs)


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


class EveSwaggerProvider(EveProvider):
    def __init__(self, token=None, adapter=None):
        self.client = esi_client_factory(token=token, spec_file=SWAGGER_SPEC_PATH)
        self.adapter = adapter or self

    def __str__(self):
        return 'esi'

    def get_alliance(self, alliance_id):
        try:
            data = self.client.Alliance.get_alliances_alliance_id(alliance_id=alliance_id).result()
            corps = self.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance_id).result()
            model = Alliance(
                id=alliance_id,
                name=data['name'],
                ticker=data['ticker'],
                corp_ids=corps,
                executor_corp_id=data['executor_corporation_id'] if 'executor_corporation_id' in data else None,
            )
            return model
        except HTTPNotFound:
            raise ObjectNotFound(alliance_id, 'alliance')

    def get_corp(self, corp_id):
        try:
            data = self.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).result()
            model = Corporation(
                id=corp_id,
                name=data['name'],
                ticker=data['ticker'],
                ceo_id=data['ceo_id'],
                members=data['member_count'],
                alliance_id=data['alliance_id'] if 'alliance_id' in data else None,
            )
            return model
        except HTTPNotFound:
            raise ObjectNotFound(corp_id, 'corporation')

    def get_character(self, character_id):
        try:
            data = self.client.Character.get_characters_character_id(character_id=character_id).result()
            model = Character(
                id=character_id,
                name=data['name'],
                corp_id=data['corporation_id'],
                alliance_id=data['alliance_id'] if 'alliance_id' in data else None,
            )
            return model
        except (HTTPNotFound, HTTPUnprocessableEntity):
            raise ObjectNotFound(character_id, 'character')

    def get_itemtype(self, type_id):
        try:
            data = self.client.Universe.get_universe_types_type_id(type_id=type_id).result()
            return ItemType(id=type_id, name=data['name'])
        except (HTTPNotFound, HTTPUnprocessableEntity):
            raise ObjectNotFound(type_id, 'type')


provider = EveSwaggerProvider()
