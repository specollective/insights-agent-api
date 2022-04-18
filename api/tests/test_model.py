import os
from django.core.exceptions import ValidationError
from django.test import TestCase
from api.models import StudyParticipant


class StudyParticipantModelTest(TestCase):
    """ Test module for Project model """

    def setUp(self):
        StudyParticipant.objects.create(
            username='example-username',
            phone_number='8455914054',
        )

    def test_study_participant_attributes(self):
        study_participant = StudyParticipant.objects.get(username='example-username')

        self.assertEqual(study_participant.username, 'example-username')
        self.assertEqual(study_participant.phone_number, '8455914054')

    def test_study_participant_phone_number_presence_validation(self):
        study_participant = StudyParticipant.objects.create(
            username='example-username2',
        )

        self.assertEqual(study_participant.username, 'example-username2')

        try:
            study_participant.full_clean()
        except ValidationError as e:
            self.assertEqual(
                e.message_dict['phone_number'][0],
                'This field cannot be blank.',
            )

    def test_study_participant_phone_number_unique_validation(self):
        study_participant1 = StudyParticipant.objects.create(
            username='example-username3',
            phone_number='+18888888888',
        )

        study_participant2 = StudyParticipant.objects.create(
            username='example-username4',
            phone_number='+18888888888',
        )

        try:
            study_participant2.full_clean()
        except ValidationError as e:
            self.assertEqual(
                e.message_dict['phone_number'][0],
                'User with this Phone number already exists.',
            )
