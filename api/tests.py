from unittest import mock
from django.test import TestCase, Client
from rest_framework import status
from .services import SmsClient


class SendMagicLinkTest(TestCase):
    """ Test module for sending a magic link via SMS"""

    @mock.patch.object(SmsClient, 'send_sms')
    def test_send_magic_link_post_request_success(self, mock_send_sms):
        client = Client()
        response = client.post(
            '/api/send_magic_link',
            '{"phone_number": "+18888888888", "name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')

    @mock.patch.object(SmsClient, 'send_sms', side_effect=Exception('Bang!'))
    def test_send_magic_link_post_request_error(self, mock_send_sms):
        client = Client()
        response = client.post(
            '/api/send_magic_link',
            '{"phone_number": "+18888888888", "name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json['message'], 'error')
