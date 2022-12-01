from json import dumps as jsonDump
from django.test import TestCase, Client
from rest_framework import status


class DataEntryAPI(TestCase):
    """ Test module for DataEntry API """

    def test_data_entry_post_request(self):
        client = Client()
        request_data = {
           "token": "sdfsew44",
           "application_name": "example",
           "tab_name": "example",
           "url": "http://localhost:3000",
           "timestamp": "2022-04-25 01:44:57.620506",
        }
        response = client.post(
            '/api/data_entries/',
            jsonDump(request_data),
            content_type="application/json"
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['application_name'], 'example')

    def test_data_entry_blank_fields_post_request(self):
        client = Client()
        request_data = {
           "token": "sdfsew44",
           "application_name": "example",
           "tab_name": "",
           "url": "",
           "timestamp": "2022-04-25 01:44:57.620506",
           "internet_connection": "online",
        }
        response = client.post(
            '/api/data_entries/',
            jsonDump(request_data),
            content_type="application/json"
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['application_name'], 'example')
        self.assertEqual(response_data['internet_connection'], 'online')

    def test_bulk_data_entry_post_request(self):
        client = Client()
        request_data = [{
           "token": "sdfsew44",
           "application_name": "example",
           "tab_name": "example",
           "url": "http://localhost:3000",
           "timestamp": "2022-04-25 01:44:57.620506",
        }]
        response = client.post(
            '/api/data_entries/',
            jsonDump(request_data),
            content_type="application/json"
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data[0]['application_name'], 'example')
