import os
import uuid
from json import dumps as dumpJson

from unittest import mock
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import TestCase, Client
from rest_framework import status

from api.models import StudyParticipant, DataEntry, Survey
from api.services import SmsClient
from rest_framework_simplejwt.tokens import RefreshToken


###############################################################
# Magic LInk API
###############################################################


@mock.patch.dict(os.environ, {"TWILIO_ACCOUNT_SID": "FAKE_TWILIO_ACCOUNT_SID"})
@mock.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "FAKE_TWILIO_AUTH_TOKEN"})
class SendMagicLinkTest(TestCase):
    """Test module for sending a magic link via SMS"""

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

###############################################################
# Data Entry API
###############################################################


class DataEntryAPI(TestCase):
    """ Test module for DataEntry API """

    def test_data_entry_post_request(self):
        client = Client()
        example_data = {
           "token": "sdfsew44",
           "application_name": "example",
           "tab_name": "example",
           "url": "http://localhost:3000",
           "timestamp": "2022-04-25 01:44:57.620506",
        }

        response = client.post(
            '/api/data_entries/',
            dumpJson(example_data),
            content_type="application/json"
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json['application_name'], 'example')

###############################################################
# Survey API
###############################################################


class SurveyAPI(TestCase):
    """ Test module for Survey API """

    # TODO: Add assertion for HTTP only auth
    def test_data_survey_post_request(self):
        client = Client()
        example_data = {
           "age": 30,
           "token": "example-token",
           "education_level": "college",
           "gender": "female",
           "hispanic_origin": True,
           "marital_status": "married",
        }

        user = User.objects.create(username='example-user-name')

        refresh = RefreshToken.for_user(user)

        response = client.post(
            '/api/surveys/',
            dumpJson(example_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json['education_level'], 'college')
