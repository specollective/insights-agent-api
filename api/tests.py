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


###########################################################
# Model Tests
###########################################################

class StudyParticipantModelTest(TestCase):
    """
    Test module for StudyParticipant model
    """

    def test_study_participant_attributes(self):
        user = User.objects.create(username='example username')
        study_participant = user.studyparticipant
        study_participant.phone_number = '8455914054'
        study_participant.save()
        self.assertEqual(study_participant.phone_number, '8455914054')


    def test_study_participant_phone_number_presence_validation(self):
        user = User.objects.create(username='example username')
        study_participant = user.studyparticipant

        try:
            study_participant.full_clean()
        except ValidationError as e:
            self.assertEqual(
                e.message_dict['phone_number'][0],
                'This field cannot be blank.',
            )


    def test_study_participant_phone_number_unique_validation(self):
        user1 = User.objects.create(username='example username')
        study_participant1 = user1.studyparticipant
        study_participant1.phone_number = '8455914054'
        study_participant1.save()

        user2 = User.objects.create(username='example username 2')
        study_participant2 = user2.studyparticipant
        study_participant2.phone_number = '8455914054'

        try:
            study_participant2.full_clean()
        except ValidationError as e:
            self.assertEqual(
                e.message_dict['phone_number'][0],
                'User with this Phone number already exists.',
            )

###############################################################
# API Tests
###############################################################

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
