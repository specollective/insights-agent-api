from api.models import Survey
from django.test import TestCase


class SurveyModelTest(TestCase):
    """
    Test module for Survey model
    """

    def test_survey_attributes(self):
        survey = Survey.objects.create(
            name="Demo",
            slug="demo",
        )

        self.assertEqual(survey.name, 'Demo')
        self.assertEqual(survey.slug, 'demo')
        self.assertEqual(len(survey.table_key), 19)
        self.assertTrue(survey.table_key.islower())