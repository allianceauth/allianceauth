from unittest import mock

from django.test import TestCase

from ..models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from ..providers import Character, Corporation, Alliance


class EveCharacterProviderManagerTestCase(TestCase):
    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_get_character(self, provider):
        expected = Character()
        provider.get_character.return_value = expected

        result = EveCharacter.provider.get_character('1234')

        self.assertEqual(expected, result)


class EveCharacterManagerTestCase(TestCase):

    class TestCharacter(Character):
        @property
        def alliance(self):
            return Alliance(id='3456', name='Test Alliance')

        @property
        def corp(self):
            return Corporation(id='2345', name='Test Corp', alliance_id='3456', ticker='0BUGS')

    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_create_character(self, provider):
        # Also covers create_character_obj
        expected = self.TestCharacter(id='1234', name='Test Character', corp_id='2345', alliance_id='3456')

        provider.get_character.return_value = expected

        result = EveCharacter.objects.create_character('1234')

        self.assertEqual(result.character_id, expected.id)
        self.assertEqual(result.character_name, expected.name)
        self.assertEqual(result.corporation_id, expected.corp.id)
        self.assertEqual(result.corporation_name, expected.corp.name)
        self.assertEqual(result.corporation_ticker, expected.corp.ticker)
        self.assertEqual(result.alliance_id, expected.alliance.id)
        self.assertEqual(result.alliance_name, expected.alliance.name)

    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_update_character(self, provider):
        # Also covers Model.update_character
        existing = EveCharacter.objects.create(
            character_id='1234',
            character_name='character.name',
            corporation_id='character.corp.id',
            corporation_name='character.corp.name',
            corporation_ticker='character.corp.ticker',
            alliance_id='character.alliance.id',
            alliance_name='character.alliance.name',
        )

        expected = self.TestCharacter(id='1234', name='Test Character', corp_id='2345', alliance_id='3456')

        provider.get_character.return_value = expected

        result = EveCharacter.objects.update_character('1234')

        self.assertEqual(result.character_id, expected.id)
        self.assertEqual(result.character_name, expected.name)
        self.assertEqual(result.corporation_id, expected.corp.id)
        self.assertEqual(result.corporation_name, expected.corp.name)
        self.assertEqual(result.corporation_ticker, expected.corp.ticker)
        self.assertEqual(result.alliance_id, expected.alliance.id)
        self.assertEqual(result.alliance_name, expected.alliance.name)

    def test_get_character_by_id(self):
        EveCharacter.objects.create(
            character_id='1234',
            character_name='character.name',
            corporation_id='character.corp.id',
            corporation_name='character.corp.name',
            corporation_ticker='character.corp.ticker',
            alliance_id='character.alliance.id',
            alliance_name='character.alliance.name',
        )

        result = EveCharacter.objects.get_character_by_id('1234')

        self.assertEqual(result.character_id, '1234')
        self.assertEqual(result.character_name, 'character.name')


class EveAllianceProviderManagerTestCase(TestCase):
    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_get_alliance(self, provider):
        expected = Alliance()
        provider.get_alliance.return_value = expected

        result = EveAllianceInfo.provider.get_alliance('1234')

        self.assertEqual(expected, result)


class EveAllianceManagerTestCase(TestCase):

    class TestAlliance(Alliance):
        def corp(self, id):
            return self._corps[id]

    @mock.patch('allianceauth.eveonline.models.EveAllianceInfo.populate_alliance')
    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_create_alliance(self, provider, populate_alliance):
        # Also covers create_alliance_obj
        expected = self.TestAlliance(id='3456', name='Test Alliance', ticker='TEST',
                                     corp_ids=['2345'], executor_corp_id='2345')

        provider.get_alliance.return_value = expected

        result = EveAllianceInfo.objects.create_alliance('3456')

        self.assertEqual(result.alliance_id, expected.id)
        self.assertEqual(result.alliance_name, expected.name)
        self.assertEqual(result.alliance_ticker, expected.ticker)
        self.assertEqual(result.executor_corp_id, expected.executor_corp_id)
        self.assertTrue(populate_alliance.called)

    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_update_alliance(self, provider):
        # Also covers Model.update_alliance
        EveAllianceInfo.objects.create(
            alliance_id='3456',
            alliance_name='alliance.name',
            alliance_ticker='alliance.ticker',
            executor_corp_id='alliance.executor_corp_id',
        )
        expected = self.TestAlliance(id='3456', name='Test Alliance', ticker='TEST',
                                     corp_ids=['2345'], executor_corp_id='2345')

        provider.get_alliance.return_value = expected

        result = EveAllianceInfo.objects.update_alliance('3456')

        # This is the only thing ever updated in code
        self.assertEqual(result.executor_corp_id, expected.executor_corp_id)


class EveCorporationProviderManagerTestCase(TestCase):
    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_get_corporation(self, provider):
        expected = Corporation()
        provider.get_corp.return_value = expected

        result = EveCorporationInfo.provider.get_corporation('2345')

        self.assertEqual(expected, result)


class EveCorporationManagerTestCase(TestCase):

    class TestCorporation(Corporation):
        @property
        def alliance(self):
            return EveAllianceManagerTestCase.TestAlliance(id='3456', name='Test Alliance', ticker='TEST',
                                                           corp_ids=['2345'], executor_corp_id='2345')

        @property
        def ceo(self):
            return EveCharacterManagerTestCase.TestCharacter(id='1234', name='Test Character',
                                                             corp_id='2345', alliance_id='3456')

    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_create_corporation(self, provider):
        # Also covers create_corp_obj
        exp_alliance = EveAllianceInfo.objects.create(
            alliance_id='3456',
            alliance_name='alliance.name',
            alliance_ticker='alliance.ticker',
            executor_corp_id='alliance.executor_corp_id',
        )

        expected = self.TestCorporation(id='2345', name='Test Corp', ticker='0BUGS',
                                        ceo_id='1234', members=1, alliance_id='3456')

        provider.get_corp.return_value = expected

        result = EveCorporationInfo.objects.create_corporation('2345')

        self.assertEqual(result.corporation_id, expected.id)
        self.assertEqual(result.corporation_name, expected.name)
        self.assertEqual(result.corporation_ticker, expected.ticker)
        self.assertEqual(result.member_count, expected.members)
        self.assertEqual(result.alliance, exp_alliance)

    @mock.patch('allianceauth.eveonline.managers.providers.provider')
    def test_create_corporation(self, provider):
        # Also covers Model.update_corporation
        exp_alliance = EveAllianceInfo.objects.create(
            alliance_id='3456',
            alliance_name='alliance.name',
            alliance_ticker='alliance.ticker',
            executor_corp_id='alliance.executor_corp_id',
        )

        EveCorporationInfo.objects.create(
            corporation_id='2345',
            corporation_name='corp.name',
            corporation_ticker='corp.ticker',
            member_count=10,
            alliance=None,
        )

        expected = self.TestCorporation(id='2345', name='Test Corp', ticker='0BUGS',
                                        ceo_id='1234', members=1, alliance_id='3456')

        provider.get_corp.return_value = expected

        result = EveCorporationInfo.objects.update_corporation('2345')

        self.assertEqual(result.corporation_id, expected.id)
        # These are the only updated props
        self.assertEqual(result.member_count, expected.members)
        self.assertEqual(result.alliance, exp_alliance)
