from __future__ import unicode_literals

try:
    # Py3
    from unittest import mock
except ImportError:
    # Py2
    import mock

from django.test import TestCase

from alliance_auth.tests.auth_utils import AuthUtils
from eveonline.providers import Character, Alliance, Corporation
from eveonline.managers import EveManager
from eveonline import tasks
from eveonline.models import EveApiKeyPair, EveCharacter
from services.managers.eve_api_manager import EveApiManager

MODULE_PATH = 'eveonline.tasks'


class EveOnlineTasksTestCase(TestCase):
    def setUp(self):
        self.user = AuthUtils.create_member('joebloggs')
        self.api_key = EveApiKeyPair.objects.create(api_id='0118999',
                                                    api_key='hunter2',
                                                    user=self.user,
                                                    sso_verified=True)

    @mock.patch(MODULE_PATH + '.EveApiManager.validate_api')
    @mock.patch(MODULE_PATH + '.EveManager.get_characters_from_api')
    def test_refresh_api_characters(self, get_characters_from_api, validate_api):
        # Arrange
        provider = mock.MagicMock()

        provider.get_alliance.return_value = Alliance(provider, 22222, 'Test Alliance', 'TEST', [11111], 11111)
        provider.get_corp.return_value = Corporation(provider, 11111, 'Test Corp', 'HERP', 12345, [12345, 23456], 22222)

        mock_api_data = [
            Character(provider, 12345, 'testchar1', 11111, 22222),
            Character(provider, 23456, 'Will beAdded', 11111, 22222)
        ]

        get_characters_from_api.return_value = mock_api_data
        validate_api.return_value = True

        EveManager.create_character_obj(mock_api_data[0], self.user, '0118999')
        EveManager.create_character_obj(Character(provider, 34567, 'deletedcharacter', 11111, 22222),
                                        self.user, '0118999')

        # Act
        tasks.refresh_api(self.api_key)

        # Assert
        self.assertTrue(EveCharacter.objects.filter(character_id='12345').exists())
        self.assertTrue(EveCharacter.objects.filter(character_id='23456').exists())
        self.assertFalse(EveCharacter.objects.filter(character_id='34567').exists())

        args, kwargs = validate_api.call_args
        self.assertEqual(args[0], self.api_key.api_id)
        self.assertEqual(args[1], self.api_key.api_key)
        self.assertEqual(args[2], self.api_key.user)

    @mock.patch(MODULE_PATH + '.EveApiManager.validate_api')
    @mock.patch(MODULE_PATH + '.EveManager')
    def test_refresh_api_evelink_exception(self, evemanager, validate_api):
        import evelink

        validate_api.side_effect = evelink.api.APIError()

        tasks.refresh_api(self.api_key)

        self.assertTrue(validate_api.called)
        self.assertFalse(evemanager.get_characters_from_api.called)
        self.assertFalse(evemanager.delete_characters_by_api_id.called)
        self.assertFalse(evemanager.delete_api_key_pair.called)

    @mock.patch(MODULE_PATH + '.EveApiManager.validate_api')
    @mock.patch(MODULE_PATH + '.EveManager')
    def test_refresh_api_invalid(self, evemanager, validate_api):
        validate_api.side_effect = EveApiManager.ApiInvalidError(self.api_key.api_id)

        tasks.refresh_api(self.api_key)

        self.assertTrue(validate_api.called)
        self.assertFalse(evemanager.get_characters_from_api.called)
        self.assertTrue(evemanager.delete_characters_by_api_id.called)
        self.assertTrue(evemanager.delete_api_key_pair.called)

    @mock.patch(MODULE_PATH + '.EveApiManager.validate_api')
    @mock.patch(MODULE_PATH + '.EveManager')
    def test_refresh_api_accountvalidationerror(self, evemanager, validate_api):
        validate_api.side_effect = EveApiManager.ApiAccountValidationError(self.api_key.api_id)

        tasks.refresh_api(self.api_key)

        self.assertTrue(validate_api.called)
        self.assertFalse(evemanager.get_characters_from_api.called)
        self.assertTrue(evemanager.delete_characters_by_api_id.called)
        self.assertTrue(evemanager.delete_api_key_pair.called)

    @mock.patch(MODULE_PATH + '.EveApiManager.validate_api')
    @mock.patch(MODULE_PATH + '.EveManager')
    def test_refresh_api_maskvalidationerror(self, evemanager, validate_api):
        validate_api.side_effect = EveApiManager.ApiMaskValidationError('12345', '1111', self.api_key.api_id)

        tasks.refresh_api(self.api_key)

        self.assertTrue(validate_api.called)
        self.assertFalse(evemanager.get_characters_from_api.called)
        self.assertTrue(evemanager.delete_characters_by_api_id.called)
        self.assertTrue(evemanager.delete_api_key_pair.called)

    @mock.patch(MODULE_PATH + '.EveApiManager.validate_api')
    @mock.patch(MODULE_PATH + '.EveManager')
    def test_refresh_api_invalid(self, evemanager, validate_api):
        validate_api.side_effect = EveApiManager.ApiServerUnreachableError(self.api_key.api_id)

        tasks.refresh_api(self.api_key)

        self.assertTrue(validate_api.called)
        self.assertFalse(evemanager.get_characters_from_api.called)
        # Lets hope we never see that again
        self.assertFalse(evemanager.delete_characters_by_api_id.called)
        self.assertFalse(evemanager.delete_api_key_pair.called)
