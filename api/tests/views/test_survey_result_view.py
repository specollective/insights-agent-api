from django.contrib.auth.models import User
from django.test import TestCase, Client
from json import dumps as jsonDump
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import SurveyResult


class SurveyAPI(TestCase):
    """Test module for Survey API"""

    # TODO: Add assertion for HTTP only auth
    def test_data_survey_post_request(self):
        self.assertEqual(SurveyResult.objects.count(), 0)

        client = Client()
        example_data = {
           'computer_use': 'school',
           'technology_compentency_level': '1',
           'internet_access': 'dial-up',
           'hispanic_origin': True,
           'household_members': '1',
           'household_computers': '1',
        }
        user = User.objects.create(username='example-user-name')
        refresh = RefreshToken.for_user(user)
        response = client.post(
            '/api/surveys',
            jsonDump(example_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        self.assertEqual(SurveyResult.objects.count(), 1)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['technology_compentency_level'], 1)

    def test_data_survey_post_request_failure(self):
        client = Client()
        example_data = {
           'computer_use': None,
           'technology_compentency_level': '1',
           'internet_access': 'dial-up',
           'hispanic_origin': True,
           'household_members': '1',
           'household_computers': '1',
        }
        user = User.objects.create(username='example-user-name')
        refresh = RefreshToken.for_user(user)
        self.assertEqual(SurveyResult.objects.count(), 0)
        response = client.post(
            '/api/surveys',
            jsonDump(example_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SurveyResult.objects.count(), 0)
