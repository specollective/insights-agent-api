import os
from json import dumps as jsonDump
from unittest import mock
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from api.models import StudyParticipant, Survey
from api.services import SmsClient, OtpClient


@mock.patch.dict(os.environ, {"TWILIO_ACCOUNT_SID": "FAKE_TWILIO_ACCOUNT_SID"})
@mock.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "FAKE_TWILIO_AUTH_TOKEN"})
class AuthenticationAPITest(TestCase):
    """Test serial number flow"""
    def test_serial_number_post_request_success(self):
        client = Client()
        survey = Survey.objects.create(name='example-name', table_key='example-slug')
        user = User.objects.create(username='Example Name')
        studyparticipant = StudyParticipant.objects.create(
            user=user,
            device_serial_number='123_test_abc_test',
        )
        studyparticipant.device_serial_number = '123_test_abc_test'
        studyparticipant.surveys.add(survey)
        studyparticipant.save()
        response = client.post(
            '/api/confirm_serial_number',
            jsonDump({
              "serial_number": '123_test_abc_test',
            }),
            content_type="application/json",
        )
        json = response.json()
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')
        self.assertEqual(json['token'], str(studyparticipant.token))

    def test_send_token_by_serial_number_request_failure(self):
        client = Client()
        user = User.objects.create(username='Example Name')
        StudyParticipant.objects.create(
            user=user,
            device_serial_number='123_test_abc_test',
        )
        response = client.post(
            '/api/confirm_serial_number',
            jsonDump({
              "serial_number": 'BAD_NUMBER',
            }),
            content_type="application/json"
        )
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(SmsClient, 'send_sms_magic_link')
    def test_send_magic_link_post_request_success(self, mock_sms):
        self.assertEqual(StudyParticipant.objects.count(), 0)
        client = Client()
        response = client.post(
            '/api/send_magic_link',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')
        self.assertEqual(StudyParticipant.objects.count(), 1)
        mock_sms.assert_called_once

    @mock.patch.object(
        SmsClient,
        'send_sms_magic_link',
        side_effect=Exception('Bang!')
    )

    def test_send_magic_link_post_request_error(self, mock_send_sms):
        self.assertEqual(StudyParticipant.objects.count(), 0)
        client = Client()
        response = client.post(
            '/api/send_magic_link',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        json = response.json()
        mock_send_sms.assert_called_once
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json['message'], 'sms failed to send')
        self.assertEqual(StudyParticipant.objects.count(), 1)

    @mock.patch.object(SmsClient, 'send_sms_magic_link')
    def test_send_magic_link_existing_num_request_error(self, mock_send_sms):
        user = User.objects.create(username='example username')
        study_participant = StudyParticipant.objects.create(
            user=user,
            phone_number='+18888888888',
        )
        self.assertEqual(StudyParticipant.objects.count(), 1)
        client = Client()
        response = client.post(
            '/api/send_magic_link',
            '{"phone_number": "+18888888888", "full_name": "John Doe"}',
            content_type="application/json"
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["error"], 'It looks like you have already signed up for this study with this phone number. Please follow the instructions given via text message. If you have not received a text message, please email tech4all@buildJUSTLY.org')
        self.assertEqual(StudyParticipant.objects.count(), 1)

    def test_confirm_magic_link_post_request_success(self):
        otp_client = OtpClient()
        client = Client()
        user = User.objects.create(username='Example Name')
        studyparticipant = StudyParticipant.objects.create(
            user=user,
            phone_number='+18888888888',
            confirmed_phone_number=False,
        )
        response = client.post(
            '/api/confirm_magic_link',
            jsonDump({
              "otp": otp_client.generate(),
              "token": str(studyparticipant.token)
            }),
            content_type="application/json"
        )
        json = response.json()
        cookies = str(response.cookies)
        self.assertTrue('HttpOnly;' in cookies)
        self.assertTrue('Set-Cookie: access_token=' in cookies)
        self.assertTrue('Domain=localhost' in cookies)
        self.assertTrue(json['access_token'] in cookies)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')
        studyparticipant.refresh_from_db()
        self.assertEqual(studyparticipant.confirmed_phone_number, True)

    def test_confirm_magic_link_post_request_failure(self):
        otp_client = OtpClient()
        client = Client()
        user = User.objects.create(username='Example Name')
        studyparticipant = StudyParticipant.objects.create(
            user=user,
            phone_number='+18888888888',
        )
        response = client.post(
            '/api/confirm_magic_link',
            jsonDump({
              "otp": 'invalid-otp',
              "token": str(studyparticipant.token)
            }),
            content_type="application/json"
        )
        json = response.json()
        studyparticipant.refresh_from_db()
        cookies = str(response.cookies)
        self.assertFalse('HttpOnly; Max-Age=1209600' in cookies)
        self.assertFalse('Set-Cookie: access_token=' in cookies)
        self.assertFalse('access_token' in json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json['message'], 'invalid access code')
        self.assertEqual(studyparticipant.confirmed_phone_number, False)

    @mock.patch.object(SmsClient, 'send_sms_access_code')
    def test_send_access_code_post_request_success(self, mock_send_sms):
        otp_client = OtpClient()
        client = Client()
        user = User.objects.create(username='Example Name')
        studyparticipant = StudyParticipant.objects.create(
            user=user,
            phone_number='+18888888888',
            confirmed_phone_number=False,
        )
        response = client.post(
            '/api/send_access_code',
            jsonDump({
              "phone_number": '+18888888888',
            }),
            content_type="application/json",
        )
        json = response.json()
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')
        self.assertEqual(json['token'], str(studyparticipant.token))
        mock_send_sms.assert_called_once

    @mock.patch.object(SmsClient, 'send_sms_access_code')
    def test_send_access_code_post_request_failure(self, mock_send_sms):
        client = Client()
        user = User.objects.create(username='Example Name')
        studyparticipant = StudyParticipant.objects.create(
            user=user,
            phone_number='+18888888888',
            confirmed_phone_number=False,
        )
        response = client.post(
            '/api/send_access_code',
            jsonDump({
              "phone_number": 'BAD_NUMBER',
            }),
            content_type="application/json"
        )
        json = response.json()
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_send_sms.assert_not_called

    def test_confirm_access_code_post_request_success(self):
        otp_client = OtpClient()
        client = Client()
        survey = Survey.objects.create(name='example-name', table_key='example-slug')
        user = User.objects.create(username='Example Name')
        studyparticipant = StudyParticipant.objects.create(
            user=user,
            phone_number='+18888888888',
            confirmed_phone_number=True,
        )
        studyparticipant.surveys.add(survey)
        studyparticipant.save()
        survey.save()

        response = client.post(
            '/api/confirm_access_code',
            jsonDump({
              "access_code": otp_client.generate(),
              "token": str(studyparticipant.token),
            }),
            content_type="application/json"
        )
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['message'], 'success')
