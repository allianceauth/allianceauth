from django.test import TestCase
from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.eveonline.models import EveAllianceInfo, EveCorporationInfo, EveCharacter
from ..models import NameFormatConfig
from ..hooks import NameFormatter
from ..modules.example.auth_hooks import ExampleService


class NameFormatterTestCase(TestCase):
    def setUp(self):
        self.member = AuthUtils.create_user('auth_member', disconnect_signals=True)

        self.alliance = EveAllianceInfo.objects.create(
            alliance_id='3456',
            alliance_name='alliance name',
            alliance_ticker='TIKR',
            executor_corp_id='2345',
        )

        self.corp = EveCorporationInfo.objects.create(
            corporation_id='2345',
            corporation_name='corp name',
            corporation_ticker='TIKK',
            member_count=10,
            alliance=self.alliance,
        )

        self.char = EveCharacter.objects.create(
            character_id='1234',
            character_name='test character',
            corporation_id='2345',
            corporation_name='test corp',
            corporation_ticker='TIKK',
            alliance_id='3456',
            alliance_name='alliance name',
            alliance_ticker='TIKR',
        )
        self.member.profile.main_character = self.char
        self.member.profile.save()

    def test_formatter_prop(self):
        config = NameFormatConfig.objects.create(
            service_name='example',
            default_to_username=False,
            format='{character_name}',
        )

        config.states.add(self.member.profile.state)

        formatter = NameFormatter(ExampleService(), self.member)

        self.assertEqual(config, formatter.formatter_config)

    def test_default_formatter(self):

        formatter = NameFormatter(ExampleService(), self.member)

        self.assertEqual(NameFormatter.DEFAULT_FORMAT, formatter.default_formatter)
        # Test the default is returned when the service has no default
        self.assertEqual(NameFormatter.DEFAULT_FORMAT, formatter.string_formatter)

    def test_get_format_data(self):
        config = NameFormatConfig.objects.create(
            service_name='example',
            default_to_username=False,
            format='{alliance_ticker}',  # Ensures that alliance_ticker is filled
        )
        config.states.add(self.member.profile.state)

        formatter = NameFormatter(ExampleService(), self.member)

        result = formatter.get_format_data()

        self.assertIn('character_name', result)
        self.assertEqual(result['character_name'], self.char.character_name)
        self.assertIn('character_id', result)
        self.assertEqual(result['character_id'], self.char.character_id)
        self.assertIn('corp_name', result)
        self.assertEqual(result['corp_name'], self.char.corporation_name)
        self.assertIn('corp_id', result)
        self.assertEqual(result['corp_id'], self.char.corporation_id)
        self.assertIn('corp_ticker', result)
        self.assertEqual(result['corp_ticker'], self.char.corporation_ticker)
        self.assertIn('alliance_name', result)
        self.assertEqual(result['alliance_name'], self.char.alliance_name)
        self.assertIn('alliance_ticker', result)
        self.assertEqual(result['alliance_ticker'], self.char.alliance_ticker)
        self.assertIn('alliance_id', result)
        self.assertEqual(result['alliance_id'], self.char.alliance_id)
        self.assertIn('username', result)
        self.assertEqual(result['username'], self.member.username)
        self.assertIn('alliance_or_corp_name', result)
        self.assertEqual(result['alliance_or_corp_name'], self.char.alliance_name)
        self.assertIn('alliance_or_corp_ticker', result)
        self.assertEqual(result['alliance_or_corp_ticker'], self.char.alliance_ticker)

    def test_format_name(self):
        config = NameFormatConfig.objects.create(
            service_name='example',
            default_to_username=False,
            format='{character_id} test {username}',
        )
        config.states.add(self.member.profile.state)
        formatter = NameFormatter(ExampleService(), self.member)

        result = formatter.format_name()

        self.assertEqual('1234 test auth_member', result)
