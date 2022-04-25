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
