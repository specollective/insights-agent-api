import os
import sys
import uuid
from json import dumps as jsonDump

from unittest import mock
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import TestCase, Client
from rest_framework import status

from api.models import StudyParticipant, DataEntry, Survey
from api.services import SmsClient, OtpClient
from rest_framework_simplejwt.tokens import RefreshToken


@mock.patch.dict(os.environ, {"TWILIO_ACCOUNT_SID": "FAKE_TWILIO_ACCOUNT_SID"})
@mock.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "FAKE_TWILIO_AUTH_TOKEN"})
class AuthenticationAPITest(TestCase):
    """Test module for sending a magic link via SMS"""

    ################################
    # Happy Path
    ################################

    @mock.patch.object(SmsClient, 'send_sms')
    def test_send_magic_link_post_request_success(self, mock_send_sms):
        client = Client()
        response = client.post(
            '/api/send_magic_link',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')


    @mock.patch.object(SmsClient, 'send_sms_magic_link')
    def test_send_access_code_post_request_error(self, mock_send_sms_magic_link):
        self.assertEqual(StudyParticipant.objects.count(), 0)

        client = Client()
        response = client.post(
            '/api/send_access_code',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')
        self.assertEqual(StudyParticipant.objects.count(), 1)
        mock_send_sms_magic_link.assert_called_once


    def test_check_access_code_post_request_success(self):
        otp_client = OtpClient()
        client = Client()

        # Set up existing study participant
        user = User.objects.create(username='Example Name')
        user.studyparticipant.phone_number = '+18888888888'
        user.confirmed_phone_number = False
        user.studyparticipant.save()

        # Make an API call
        response = client.post(
            '/api/check_access_code',
            jsonDump({
              "otp": otp_client.generate(),
              "token": str(user.studyparticipant.token)
            }),
            content_type="application/json"
        )
        json = response.json()
        cookies = str(response.cookies)

        # Assert that http only headers are being set
        self.assertTrue('HttpOnly;' in cookies)
        self.assertTrue('Set-Cookie: access_token=' in cookies)
        self.assertTrue(json['access_token'] in cookies)

        # Assert that the request responds with the expected data.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')
        self.assertEqual(len(json['survey_token']), 140)
        self.assertEqual(len(json['refresh_token']), 229)

        # Assert that we update the study participants confirmed_phone_number field.
        user.studyparticipant.refresh_from_db()
        self.assertEqual(user.studyparticipant.confirmed_phone_number, True)

    ################################
    # Errors Cases
    ################################

    @mock.patch.object(SmsClient, 'send_sms', side_effect=Exception('Bang!'))
    def test_send_magic_link_post_request_error(self, mock_send_sms):
        client = Client()
        response = client.post(
            '/api/send_magic_link',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        mock_send_sms.assert_called_once
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json['message'], 'error')


    @mock.patch.object(SmsClient, 'send_sms_magic_link', side_effect=Exception('Bang!'))
    def test_send_magic_link_post_request_error(self, mock_send_sms):
        self.assertEqual(StudyParticipant.objects.count(), 0)

        client = Client()
        response = client.post(
            '/api/send_access_code',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        mock_send_sms.assert_called_once
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json['message'], 'sms failed to send')
        self.assertEqual(StudyParticipant.objects.count(), 1)


    @mock.patch.object(SmsClient, 'send_sms_magic_link')
    def test_send_access_code_with_existing_number_request_error(self, mock_send_sms):
        user = User.objects.create(username='example username')
        study_participant = user.studyparticipant
        study_participant.phone_number = '+18888888888'
        study_participant.save()

        self.assertEqual(StudyParticipant.objects.count(), 1)

        client = Client()
        response = client.post(
            '/api/send_access_code',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data['message'], 'invalid credentials')

        # Does not create a new study participant
        self.assertEqual(StudyParticipant.objects.count(), 1)


    def test_check_access_code_post_request_failure(self):
        otp_client = OtpClient()
        client = Client()

        user = User.objects.create(username='Example Name')
        user.studyparticipant.phone_number = '+18888888888'
        user.studyparticipant.save()

        response = client.post(
            '/api/check_access_code',
            jsonDump({
              "otp": 'invalid-otp',
              "token": str(user.studyparticipant.token)
            }),
            content_type="application/json"
        )
        json = response.json()

        user.studyparticipant.refresh_from_db()

        cookies = str(response.cookies)

        print(cookies)

        self.assertFalse('HttpOnly; Max-Age=1209600' in cookies)
        self.assertFalse('Set-Cookie: access_token=' in cookies)
        self.assertFalse('access_token' in json)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json['message'], 'invalid access code')
        self.assertEqual(user.studyparticipant.confirmed_phone_number, False)
