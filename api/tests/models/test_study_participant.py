from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from api.models import StudyParticipant


class StudyParticipantModelTest(TestCase):
    """
    Test module for StudyParticipant model
    """
    def test_study_participant_attributes(self):
        user = User.objects.create(username='example username')
        study_participant = StudyParticipant.objects.create(
            user=user,
            token='TOKEN',
            phone_number='+18888888888',
        )
        self.assertEqual(study_participant.phone_number, '+18888888888')
        self.assertEqual(study_participant.user, user)

    def test_study_participant_attributes(self):
        study_participant = StudyParticipant.objects.create(
            token='TOKEN'
        )
        study_participant.save()
        self.assertEqual(study_participant.token, 'TOKEN')

    ## To do: Uncomment once we add custom validation to study_participant
    ##          This validation is not business critical
    # def test_study_participant_phone_number_presence_validation(self):
    #     user = User.objects.create(username='example username')
    #     study_participant = user.studyparticipant

    #     try:
    #         study_participant.full_clean()
    #     except ValidationError as e:
    #         self.assertEqual(
    #             e.message_dict['phone_number'][0],
    #             'This field cannot be blank.',
    #         )

    def test_study_participant_phone_number_unique_validation(self):
        user1 = User.objects.create(username='example username')
        study_participant1 = StudyParticipant.objects.create(
            user=user1,
            full_name='full name',
            phone_number='+18888888888',
        )

        user2 = User.objects.create(username='example username 2')
        study_participant2 = StudyParticipant.objects.create(
            user=user2,
            full_name='full name',
            phone_number='+18888888888',
        )

        try:
            study_participant2.full_clean()
        except ValidationError as e:
            self.assertEqual(
                e.message_dict['phone_number'][0],
                'User with this Phone number already exists.',
            )
