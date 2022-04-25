import os
from json import dumps as jsonDump
from unittest import mock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from api.services import SmsClient, OtpClient
from api.models import StudyParticipant


@mock.patch.dict(os.environ, {"TWILIO_ACCOUNT_SID": "FAKE_TWILIO_ACCOUNT_SID"})
@mock.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "FAKE_TWILIO_AUTH_TOKEN"})
class SendAccessCodeTest(TestCase):
    """
    Test module for sending an access code via SMS
    """
    @mock.patch.object(SmsClient, 'send_sms_magic_link')
    def test_send_access_code_post_request_success(self, send_sms_magic_link):
        client = Client()
        response = client.post(
            '/api/send_access_code',
            '{"phone_number": "+18888888888", "name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        studyparticipant = StudyParticipant.objects.first()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['status'], 'success')
        self.assertEqual(json['token'], studyparticipant.token)
        send_sms_magic_link.assert_called_once

# @mock.patch.object(SmsClient, 'send_sms', side_effect=Exception('Bang!'))
# def test_send_access_code_post_request_error(self, mock_send_sms):
#     client = Client()
#     response = client.post(
#         '/api/send_access_code',
#         '{"phone_number": "+18888888888", "name": "John Doe"}',
#         content_type="application/json"
#     )
#     json = response.json()
#     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     self.assertEqual(json['status'], 'error')
#
#
# @mock.patch.object(SmsClient, 'send_sms', side_effect=Exception('Bang!'))
# def test_check_access_code_post_request_success(self, mock_send_sms):
#     otp_client = OtpClient()
#     client = Client()
#
#     user = User.objects.create(username='Example Name')
#     user.studyparticipant.phone_number = '+18888888888'
#     user.studyparticipant.save()
#
#     response = client.post(
#         '/api/check_access_code',
#         jsonDump({
#           "otp": otp_client.generate(),
#           "token": str(user.studyparticipant.token)
#         }),
#         content_type="application/json"
#     )
#
#     json = response.json()
#     self.assertEqual(response.status_code, status.HTTP_200_OK)
#     self.assertEqual(json['status'], 'success')
