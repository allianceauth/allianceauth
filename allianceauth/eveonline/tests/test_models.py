from django.test import TestCase

from ..models import EveCharacter, EveCorporationInfo, EveAllianceInfo


class EveCharacterTestCase(TestCase):
    def test_corporation_prop(self):
        """
        Test that the correct corporation is returned by the corporation property
        """
        character = EveCharacter.objects.create(
            character_id='1234',
            character_name='character.name',
            corporation_id='2345',
            corporation_name='character.corp.name',
            corporation_ticker='character.corp.ticker',
            alliance_id='character.alliance.id',
            alliance_name='character.alliance.name',
        )

        expected = EveCorporationInfo.objects.create(
            corporation_id='2345',
            corporation_name='corp.name',
            corporation_ticker='corp.ticker',
            member_count=10,
            alliance=None,
        )

        incorrect = EveCorporationInfo.objects.create(
            corporation_id='9999',
            corporation_name='corp.name1',
            corporation_ticker='corp.ticker1',
            member_count=10,
            alliance=None,
        )

        self.assertEqual(character.corporation, expected)
        self.assertNotEqual(character.corporation, incorrect)

    def test_corporation_prop_exception(self):
        """
        Check that an exception is raised when the expected
        object is not in the database
        """
        character = EveCharacter.objects.create(
            character_id='1234',
            character_name='character.name',
            corporation_id='2345',
            corporation_name='character.corp.name',
            corporation_ticker='character.corp.ticker',
            alliance_id='character.alliance.id',
            alliance_name='character.alliance.name',
        )

        with self.assertRaises(EveCorporationInfo.DoesNotExist):
            result = character.corporation

    def test_alliance_prop(self):
        """
        Test that the correct alliance is returned by the alliance property
        """
        character = EveCharacter.objects.create(
            character_id='1234',
            character_name='character.name',
            corporation_id='2345',
            corporation_name='character.corp.name',
            corporation_ticker='character.corp.ticker',
            alliance_id='3456',
            alliance_name='character.alliance.name',
        )

        expected = EveAllianceInfo.objects.create(
            alliance_id='3456',
            alliance_name='alliance.name',
            alliance_ticker='alliance.ticker',
            executor_corp_id='alliance.executor_corp_id',
        )

        incorrect = EveAllianceInfo.objects.create(
            alliance_id='9001',
            alliance_name='alliance.name1',
            alliance_ticker='alliance.ticker1',
            executor_corp_id='alliance.executor_corp_id1',
        )

        self.assertEqual(character.alliance, expected)
        self.assertNotEqual(character.alliance, incorrect)

    def test_alliance_prop_exception(self):
        """
        Check that an exception is raised when the expected
        object is not in the database
        """
        character = EveCharacter.objects.create(
            character_id='1234',
            character_name='character.name',
            corporation_id='2345',
            corporation_name='character.corp.name',
            corporation_ticker='character.corp.ticker',
            alliance_id='3456',
            alliance_name='character.alliance.name',
        )

        with self.assertRaises(EveAllianceInfo.DoesNotExist):
            result = character.alliance

    def test_alliance_prop_none(self):
        """
        Check that None is returned when the character has no alliance
        """
        character = EveCharacter.objects.create(
            character_id='1234',
            character_name='character.name',
            corporation_id='2345',
            corporation_name='character.corp.name',
            corporation_ticker='character.corp.ticker',
            alliance_id=None,
            alliance_name=None,
        )

        self.assertIsNone(character.alliance)
