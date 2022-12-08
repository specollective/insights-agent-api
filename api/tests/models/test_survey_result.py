from django.contrib.auth.models import User
from django.test import TestCase
from api.models import Survey, SurveyResult

class SurveyResultModelTest(TestCase):
    """
    Test module for SurveyResult model
    """
    def setUp(self):
        user = User.objects.create(username='example username')
        self.participant = user.studyparticipant
        self.survey = Survey.objects.create()

    def test_survey_result_attributes(self):
        survey_result = SurveyResult.objects.create(
            participant=self.participant,
            survey=self.survey,     
            token='token123',
            hispanic_origin=True,
            computer_use='gaming,school,creativity,business,family,gain-new-skills,job-search',
            household_computers=4,
            household_members=5,
            internet_access='satellite',
            technology_compentency_level=3
        )

        self.assertEqual(survey_result.participant, self.participant)
        self.assertEqual(survey_result.survey, self.survey)
        self.assertEqual(survey_result.token, 'token123')
        self.assertEqual(survey_result.hispanic_origin, True)
        self.assertEqual(survey_result.computer_use, 'gaming,school,creativity,business,family,gain-new-skills,job-search')
        self.assertEqual(survey_result.household_computers, 4)
        self.assertEqual(survey_result.household_members, 5)
        self.assertEqual(survey_result.internet_access, 'satellite')
        self.assertEqual(survey_result.technology_compentency_level, 3)
