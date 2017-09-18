from unittest import mock

import requests_mock
import json
import datetime

from django.test import TestCase
from django.utils.timezone import make_aware, utc

from allianceauth.fleetup.managers import FleetUpManager


class FleetupManagerTestCase(TestCase):
    def setUp(self):
        pass

    def test__request_cache_key(self):

        cache_key = FleetUpManager._request_cache_key('testurl')

        self.assertEqual('FLEETUP_ENDPOINT_a39562b6ef5b858220be13d2adb61d3f10cf8d61',
                         cache_key)

    @mock.patch('allianceauth.fleetup.managers.cache')
    @requests_mock.Mocker()
    def test_get_endpoint(self, cache, m):
        url = "http://example.com/test/endpoint/"
        json_data = {'data': "123456", 'CachedUntilUTC': '/Date(1493896236163)/', 'Success': True}
        m.register_uri('GET', url,
                       text=json.dumps(json_data))

        cache.get.return_value = None  # No cached value

        # Act
        result = FleetUpManager.get_endpoint(url)

        # Assert
        self.assertTrue(cache.get.called)
        self.assertTrue(cache.set.called)
        args, kwargs = cache.set.call_args
        self.assertDictEqual(json_data, args[1])

        self.assertDictEqual(json_data, result)

    @mock.patch('allianceauth.fleetup.managers.cache')
    @requests_mock.Mocker()
    def test_get_endpoint_error(self, cache, m):
        url = "http://example.com/test/endpoint/"
        json_data = {'data': [], 'Success': False}
        m.register_uri('GET', url,
                       text=json.dumps(json_data),
                       status_code=400)

        cache.get.return_value = None  # No cached value

        # Act
        result = FleetUpManager.get_endpoint(url)

        # Assert
        self.assertTrue(cache.get.called)
        self.assertFalse(cache.set.called)
        self.assertIsNone(result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_members(self, get_endpoint):

        get_endpoint.return_value = {"Data": [
            {
                'UserId': 1234,
                'EveCharName': 'test_name',
                'EveCharId': 5678,
                'Corporation': 'test_corporation',
            }
        ]}

        # Act
        result = FleetUpManager.get_fleetup_members()

        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0],
                         FleetUpManager.BASE_URL + '/GroupCharacters/' +
                         FleetUpManager.GROUP_ID)
        expected_result = {
            1234: {
                'user_id': 1234,
                'char_name': 'test_name',
                'char_id': 5678,
                'corporation': 'test_corporation',
            }
        }
        self.assertDictEqual(expected_result, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_members()

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': []}

        # Act
        result = FleetUpManager.get_fleetup_members()

        # Assert
        self.assertDictEqual({}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_operations(self, get_endpoint):

        get_endpoint.return_value = {"Data": [
            {
                'Subject': 'test_operation',
                'StartString': '2017-05-06 11:11:11',
                'EndString': '2017-05-06 12:12:12',
                'OperationId': 1234,
                'Location': 'Jita',
                'LocationInfo': '4-4',
                'Details': 'This is a test operation',
                'Url': 'http://example.com/1234',
                'Doctrines': 'Foxcats',
                'Organizer': 'Example FC'
            }
        ]}

        # Act
        result = FleetUpManager.get_fleetup_operations()
        self.maxDiff = None
        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0],
                         FleetUpManager.BASE_URL + '/Operations/' +
                         FleetUpManager.GROUP_ID)
        expected_result = {
            '2017-05-06 11:11:11': {
                'subject': 'test_operation',
                'start': make_aware(datetime.datetime(2017, 5, 6, 11, 11, 11), utc),
                'end': make_aware(datetime.datetime(2017, 5, 6, 12, 12, 12), utc),
                'operation_id': 1234,
                'location': 'Jita',
                'location_info': '4-4',
                'details': 'This is a test operation',
                'url': 'http://example.com/1234',
                'doctrine': 'Foxcats',
                'organizer': 'Example FC'
            }
        }
        self.assertDictEqual(expected_result, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_operations()

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': []}

        # Act
        result = FleetUpManager.get_fleetup_operations()

        # Assert
        self.assertDictEqual({}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_timers(self, get_endpoint):

        get_endpoint.return_value = {"Data": [
            {
                'ExpiresString': '2017-05-06 11:11:11',
                'SolarSystem': 'Jita',
                'Planet': '4',
                'Moon': '4',
                'Owner': 'Caldari Navy',
                'Type': 'Caldari Station',
                'TimerType': 'Armor',
                'Notes': 'Burn Jita?'
            }
        ]}

        # Act
        result = FleetUpManager.get_fleetup_timers()

        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0],
                         FleetUpManager.BASE_URL + '/Timers/' +
                         FleetUpManager.GROUP_ID)
        expected_result = {
            '2017-05-06 11:11:11': {
                'expires': make_aware(datetime.datetime(2017, 5, 6, 11, 11, 11), utc),
                'solarsystem': 'Jita',
                'planet': '4',
                'moon': '4',
                'owner': 'Caldari Navy',
                'type': 'Caldari Station',
                'timer_type': 'Armor',
                'notes': 'Burn Jita?'
            }
        }
        self.assertDictEqual(expected_result, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_timers()

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': []}

        # Act
        result = FleetUpManager.get_fleetup_timers()

        # Assert
        self.assertDictEqual({}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_doctrines(self, get_endpoint):

        get_endpoint.return_value = {"Data": [
            {
                'TestData': True
            }
        ]}

        # Act
        result = FleetUpManager.get_fleetup_doctrines()

        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0],
                         FleetUpManager.BASE_URL + '/Doctrines/' +
                         FleetUpManager.GROUP_ID)
        expected_result = {
            'fleetup_doctrines': [{
                'TestData': True
            }]
        }
        self.assertDictEqual(expected_result, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_doctrines()

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': []}

        # Act
        result = FleetUpManager.get_fleetup_doctrines()

        # Assert
        self.assertDictEqual({"fleetup_doctrines": []}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_doctrine(self, get_endpoint):

        get_endpoint.return_value = {"Data": [
            {
                'TestData': True
            }
        ]}

        # Act
        result = FleetUpManager.get_fleetup_doctrine(1234)

        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0],
                         FleetUpManager.BASE_URL + '/DoctrineFittings/1234')
        expected_result = {
            'fitting_doctrine': {'Data': [{
                'TestData': True
            }]}
        }
        self.assertDictEqual(expected_result, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_doctrine(1234)

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': []}

        # Act
        result = FleetUpManager.get_fleetup_doctrine(1234)

        # Assert
        self.assertDictEqual({"fitting_doctrine": {'Data': []}}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_fittings(self, get_endpoint):

        get_endpoint.return_value = {"Data": [
            {
                'FittingId': 1234,
                'Name': 'Foxcat',
                'EveTypeId': 17726,
                'HullType': 'Battleship',
                'ShipType': 'Apocalypse Navy Issue',
                'EstPrice': 500000000,
                'Faction': 'Amarr',
                'Categories': ["Armor", "Laser"],
                'LastUpdatedString': '2017-05-06 11:11:11',
            }
        ]}

        # Act
        result = FleetUpManager.get_fleetup_fittings()

        # Asset
        self.assertTrue(get_endpoint.called)
        expected_result = {
            1234: {
                'fitting_id': 1234,
                'name': 'Foxcat',
                'icon_id': 17726,
                'hull': 'Battleship',
                'shiptype': 'Apocalypse Navy Issue',
                'estimated': 500000000,
                'faction': 'Amarr',
                'categories': ["Armor", "Laser"],
                'last_update': make_aware(datetime.datetime(2017, 5, 6, 11, 11, 11), utc)
            }
        }
        self.assertDictEqual(expected_result, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_fittings()

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': []}

        # Act
        result = FleetUpManager.get_fleetup_fittings()

        # Assert
        self.assertDictEqual({}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_fitting(self, get_endpoint):

        get_endpoint.return_value = {"Data":
            {
                'FittingData': [{}]
            }
        }

        # Act
        result = FleetUpManager.get_fleetup_fitting(1234)

        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0], FleetUpManager.BASE_URL + '/Fitting/1234')
        expected_result = {
            'fitting_data': {
                'FittingData': [{}]
            }
        }
        self.assertDictEqual(expected_result, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_fitting(1234)

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': {}}

        # Act
        result = FleetUpManager.get_fleetup_fitting(1234)

        # Assert
        self.assertDictEqual({"fitting_data": {}}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_doctrineid(self, get_endpoint):

        get_endpoint.return_value = {
            "Data": {
                'Doctrines': [{'DoctrineId': 4567}]
            }
        }

        # Act
        result = FleetUpManager.get_fleetup_doctrineid(1234)

        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0], FleetUpManager.BASE_URL + '/Fitting/1234')

        self.assertEqual(4567, result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_doctrineid(1234)

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': {}}

        # Act
        result = FleetUpManager.get_fleetup_doctrineid(1234)

        # Assert
        self.assertDictEqual({}, result)

    @mock.patch('allianceauth.fleetup.managers.FleetUpManager.get_endpoint')
    def test_get_fleetup_fitting_eft(self, get_endpoint):

        get_endpoint.return_value = {
            "Data": {
                'FittingData': '[Apocalypse Navy Issue, Foxcat]'
            }
        }

        # Act
        result = FleetUpManager.get_fleetup_fitting_eft(1234)

        # Asset
        self.assertTrue(get_endpoint.called)
        args, kwargs = get_endpoint.call_args
        self.assertEqual(args[0], FleetUpManager.BASE_URL + '/Fitting/1234/eft')

        self.assertDictEqual({"fitting_eft": '[Apocalypse Navy Issue, Foxcat]'},
                             result)

        # Test None response
        # Arrange
        get_endpoint.return_value = None

        # Act
        result = FleetUpManager.get_fleetup_fitting_eft(1234)

        # Assert
        self.assertIsNone(result)

        # Test Empty response
        # Arrange
        get_endpoint.return_value = {'Data': {}}

        # Act
        result = FleetUpManager.get_fleetup_fitting_eft(1234)

        # Assert
        self.assertDictEqual({"fitting_eft": {}}, result)
