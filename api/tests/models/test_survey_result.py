from django.test import TestCase
from api.models import Survey, SurveyResult

class SurveyResultModelTest(TestCase):
    """
    Test module for SurveyResult model
    """
    def setUp(self):
        self.survey = Survey.objects.create()

    def test_survey_result_attributes(self):
        survey_result = SurveyResult.objects.create(
            survey=self.survey,     
            token='token123',
            hispanic_origin=True,
            computer_use='gaming,school,creativity,business,family,gain-new-skills,job-search',
            household_computers=4,
            household_members=5,
            internet_access='satellite',
            computer_difficulty_level=1,
            solve_computer_problems_level=1,
            handle_computer_problems_level=1,
            computer_acting_up_level=1,
            complex_computer_level=1,
            race="race"
        )

        self.assertEqual(survey_result.survey, self.survey)
        self.assertEqual(survey_result.token, 'token123')
        self.assertEqual(survey_result.hispanic_origin, True)
        self.assertEqual(survey_result.computer_use, 'gaming,school,creativity,business,family,gain-new-skills,job-search')
        self.assertEqual(survey_result.household_computers, 4)
        self.assertEqual(survey_result.household_members, 5)
        self.assertEqual(survey_result.internet_access, 'satellite')
        self.assertEqual(survey_result.computer_difficulty_level, 1)
        self.assertEqual(survey_result.solve_computer_problems_level, 1)
        self.assertEqual(survey_result.handle_computer_problems_level, 1)
        self.assertEqual(survey_result.computer_acting_up_level, 1)
        self.assertEqual(survey_result.complex_computer_level, 1)
        self.assertEqual(survey_result.race, 'race')
