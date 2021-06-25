from datetime import datetime

import requests
import unittest

from unittest import mock
from abc import ABCMeta, abstractmethod
from app.app import app


class AbstractTestAPI(object, metaclass=ABCMeta):
    API_URL = '/conference/api/'
    OBJECT_URL: str
    ID: int
    NUMBER_OF_OBJECTS: int
    JSON_NEW_OBJECT: dict
    ROLE_ID: int
    user = mock.MagicMock()

    def setUp(self) -> None:
        print('==> Set up')
        self.user.__repr__ = lambda self: 'admin'
        self.app = app.test_client()

    def tearDown(self) -> None:
        print('==> Tearing down after tests!')

    @mock.patch('flask_login.utils._get_user')
    def test_get_all_objects(self, current_user):
        self.user.role_id = 1
        current_user.return_value = self.user
        r = self.app.get(self.OBJECT_URL)
        assert 200 == r.status_code
        assert self.NUMBER_OF_OBJECTS == len(r.json['json_list'])

    @mock.patch('flask_login.utils._get_user')
    def test_get_object(self, current_user):
        self.user.role_id = self.ROLE_ID
        current_user.return_value = self.user
        r = self.app.get(f'{self.OBJECT_URL}/{self.ID}')
        assert 200 == r.status_code
        assert self.ID == r.json['id']

    @mock.patch('flask_login.utils._get_user')
    def test_create_object(self, current_user):
        self.user.role_id = self.ROLE_ID
        current_user.return_value = self.user
        r = self.app.post(self.OBJECT_URL, json=self.JSON_NEW_OBJECT)
        assert 201 == r.status_code
        assert self.NUMBER_OF_OBJECTS + 1 == len(r.json['json_list'])

    @abstractmethod
    def test_update_object(self):
        pass

    @mock.patch('flask_login.utils._get_user')
    def test_delete_object(self, current_user):
        self.user.role_id = 1
        current_user.return_value = self.user
        r = self.app.delete(f'{self.OBJECT_URL}/{self.ID}')
        assert 200 == r.status_code
        assert r.json['result'] is True


class TestPresentation(AbstractTestAPI, unittest.TestCase):
    OBJECT_URL = f'{AbstractTestAPI.API_URL}presentations'
    ID = 3
    JSON_NEW_OBJECT = {'name': 'new presentation', 'text': 'new text'}
    NUMBER_OF_OBJECTS = 3
    ROLE_ID = 2

    @mock.patch('flask_login.utils._get_user')
    def test_update_object(self, current_user):
        self.user.id = 2
        current_user.return_value = self.user
        new_name = 'new presentation'
        presentation_json = {'name': new_name, 'text': 'new text'}
        r = self.app.put(f'{self.OBJECT_URL}/1', json=presentation_json)
        assert 200 == r.status_code
        assert 1 == r.json['id']
        assert new_name == r.json['name']

    @mock.patch('flask_login.utils._get_user')
    def test_create_presentation_by_invalid_user(self, current_user):
        self.user.role_id = 1
        current_user.return_value = self.user
        r = self.app.post(f'{self.OBJECT_URL}', json=self.JSON_NEW_OBJECT)
        assert 403 == r.status_code

    @mock.patch('flask_login.utils._get_user')
    def test_not_found_presentation_by_id(self, current_user):
        self.user.role_id = 1
        current_user.return_value = self.user
        r = self.app.get(f'{self.OBJECT_URL}/10')
        assert 404 == r.status_code

    @mock.patch('flask_login.utils._get_user')
    def test_update_presentation_by_invalid_user(self, current_user):
        self.user.id = 1
        current_user.return_value = self.user
        presentation_json = {'name': 'new name', 'text': 'new text'}
        r = self.app.put(f'{self.OBJECT_URL}/1', json=presentation_json)
        print(r.status_code)
        assert 403 == r.status_code

    @mock.patch('flask_login.utils._get_user')
    def test_delete_presentation_by_invalid_user(self, current_user):
        self.user.role_id = 2
        current_user.return_value = self.user
        r = self.app.delete(f'{self.OBJECT_URL}/1')
        assert 403 == r.status_code


class TestRoom(AbstractTestAPI, unittest.TestCase):
    OBJECT_URL = f'{AbstractTestAPI.API_URL}rooms'
    ID = 3
    JSON_NEW_OBJECT = {'name': 'new room'}
    NUMBER_OF_OBJECTS = 3
    ROLE_ID = 1

    @mock.patch('flask_login.utils._get_user')
    def test_update_object(self, current_user):
        self.user.role_id = 1
        current_user.return_value = self.user
        new_name = 'new room'
        room_json = {'name': new_name}
        r = self.app.put(f'{self.OBJECT_URL}/{self.ID}', json=room_json)
        assert 200 == r.status_code
        assert self.ID == r.json['id']
        assert new_name == r.json['name']

    @mock.patch('flask_login.utils._get_user')
    def test_actions_with_rooms_by_invalid_user(self, current_user):
        self.user.role_id = 2
        current_user.return_value = self.user
        r = self.app.get(f'{self.OBJECT_URL}/{self.ID}')
        assert 403 == r.status_code
        r = self.app.get(f'{self.OBJECT_URL}')
        assert 403 == r.status_code


class TestSchedule(AbstractTestAPI, unittest.TestCase):
    OBJECT_URL = f'{AbstractTestAPI.API_URL}schedule'
    ID = 2
    JSON_NEW_OBJECT = {'date_start': '2020-02-03', 'room_id': 1, 'presentation_id': 2}
    NUMBER_OF_OBJECTS = 2
    ROLE_ID = 1

    @mock.patch('flask_login.utils._get_user')
    def test_update_object(self, current_user):
        self.user.role_id = 1
        current_user.return_value = self.user
        new_date = '2021-03-04'
        presentation_json = {'date_start': new_date, 'room_id': 2, 'presentation_id': 2}
        r = self.app.put(f'{self.OBJECT_URL}/{self.ID}', json=presentation_json)
        assert 200 == r.status_code
        assert self.ID == r.json['id']

    @mock.patch('flask_login.utils._get_user')
    def test_create_record_with_invalid_data(self, current_user):
        self.user.role_id = 1
        current_user.return_value = self.user
        r = self.app.post(f'{self.OBJECT_URL}')
        assert 400 == r.status_code

        r = self.app.post(f'{self.OBJECT_URL}', json={'room_id': 1})
        assert 400 == r.status_code

    @mock.patch('flask_login.utils._get_user')
    def test_actions_with_schedule_by_invalid_user(self, current_user):
        self.user.role_id = 3
        current_user.return_value = self.user
        r = self.app.put(f'{self.OBJECT_URL}/1')
        assert 403 == r.status_code

        r = self.app.post(f'{self.OBJECT_URL}')
        assert 403 == r.status_code
