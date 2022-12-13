from django.contrib.auth.models import User
from django.test import TestCase, Client
from json import dumps as jsonDump
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import SurveyResult, Survey


class SurveyResultAPI(TestCase):
    """Test module for Survey Result API"""

    def setUp(self):
        self.user = User.objects.create(username='example-user-name')
        self.survey = Survey.objects.create()

    def test_data_survey_post_request(self):
        self.assertEqual(SurveyResult.objects.count(), 0)

        client = Client()
        example_data = {
            'token': 'token123',
            'survey_id': self.survey.id,
            'computer_use': 'school',
            'technology_compentency_level': '1',
            'internet_access': 'dial-up',
            'hispanic_origin': True,
            'household_members': '1',
            'household_computers': '1',
        }
        refresh = RefreshToken.for_user(self.user)
        response = client.post(
            '/api/survey_results',
            jsonDump(example_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        self.assertEqual(SurveyResult.objects.count(), 1)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['technology_compentency_level'], 1)
        self.assertEqual(response_data['survey'], self.survey.id)

    def test_data_survey_post_request_failure(self):
        client = Client()
        example_data = {
            'token': 'token123',
            'survey_id': self.survey.id,
            'computer_use': None,
            'technology_compentency_level': '1',
            'internet_access': 'dial-up',
            'hispanic_origin': True,
            'household_members': '1',
            'household_computers': '1',
        }
        refresh = RefreshToken.for_user(self.user)
        self.assertEqual(SurveyResult.objects.count(), 0)
        response = client.post(
            '/api/survey_results',
            jsonDump(example_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SurveyResult.objects.count(), 0)
