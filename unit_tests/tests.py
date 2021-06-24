import requests
import unittest
from abc import ABCMeta, abstractmethod


class AbstractTestAPI(object, metaclass=ABCMeta):
    API_URL = 'http://127.0.0.1:5000/conference/api/'
    OBJECT_URL: str
    ID: int
    NUMBER_OF_OBJECTS: int
    JSON_NEW_OBJECT: dict

    def test_get_all_objects(self):
        r = requests.get(self.OBJECT_URL)
        assert 200 == r.status_code
        assert self.NUMBER_OF_OBJECTS == len(r.json()['json_list'])

    def test_get_object(self):
        r = requests.get(f'{self.OBJECT_URL}/{self.ID}')
        assert 200 == r.status_code
        assert self.ID == r.json()['id']

    def test_create_object(self):
        r = requests.post(self.OBJECT_URL, json=self.JSON_NEW_OBJECT)
        assert 201 == r.status_code
        assert self.NUMBER_OF_OBJECTS+1 == len(r.json()['json_list'])

    @abstractmethod
    def test_update_object(self):
        pass

    def test_delete_object(self):
        r = requests.delete(f'{self.OBJECT_URL}/{self.ID}')
        assert 200 == r.status_code
        assert r.json()['result'] is True


class TestPresentation(AbstractTestAPI, unittest.TestCase):
    OBJECT_URL = f'{AbstractTestAPI.API_URL}presentations'
    ID = 3
    JSON_NEW_OBJECT = {'name': 'new presentation', 'text': 'new text'}
    NUMBER_OF_OBJECTS = 3

    def test_update_object(self):
        new_name = 'new presentation'
        presentation_json = {'name': new_name, 'text': 'new text'}
        r = requests.put(f'{self.OBJECT_URL}/{self.ID}', json=presentation_json)
        assert 200 == r.status_code
        assert self.ID == r.json()['id']
        assert new_name == r.json()['name']


class TestRoom(AbstractTestAPI, unittest.TestCase):
    OBJECT_URL = f'{AbstractTestAPI.API_URL}rooms'
    ID = 3
    JSON_NEW_OBJECT = {'name': 'new room'}
    NUMBER_OF_OBJECTS = 3

    def test_update_object(self):
        new_name = 'new room'
        room_json = {'name': new_name}
        r = requests.put(f'{self.OBJECT_URL}/{self.ID}', json=room_json)
        assert 200 == r.status_code
        assert self.ID == r.json()['id']
        assert new_name == r.json()['name']


class TestSchedule(AbstractTestAPI, unittest.TestCase):
    OBJECT_URL = f'{AbstractTestAPI.API_URL}schedule'
    ID = 2
    JSON_NEW_OBJECT = {'date_start': '2020-02-03', 'room_id': 1, 'presentation_id': 2}
    NUMBER_OF_OBJECTS = 2

    def test_update_object(self):
        new_date = '2021-03-04'
        presentation_json = {'date_start': '2020-02-03', 'room_id': 2, 'presentation_id': 2}
        r = requests.put(f'{self.OBJECT_URL}/{self.ID}', json=presentation_json)
        assert 200 == r.status_code
        assert self.ID == r.json()['id']
        assert new_date == r.json()['date_start']
