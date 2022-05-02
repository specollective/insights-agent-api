import os
import uuid
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from json import dumps as jsonDump
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest import mock
from api.models import StudyParticipant, DataEntry, Survey
from api.services import SmsClient, OtpClient


class SurveyAPI(TestCase):
    """Test module for Survey API"""

    # TODO: Add assertion for HTTP only auth
    def test_data_survey_post_request(self):
        self.assertEqual(Survey.objects.count(), 0)

        client = Client()
        example_data = {
           'age': 30,
           'token': 'example-token',
           'education_level': 'college',
           'gender': 'female',
           'hispanic_origin': True,
           'marital_status': 'married',
        }
        user = User.objects.create(username='example-user-name')
        refresh = RefreshToken.for_user(user)
        response = client.post(
            '/api/surveys',
            jsonDump(example_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        self.assertEqual(Survey.objects.count(), 1)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['education_level'], 'college')

    def test_data_survey_post_request_failure(self):
        client = Client()
        example_data = {
           'age': 30,
           'token': 'example-token',
           'education_level': None,
           'gender': 'female',
           'hispanic_origin': True,
           'marital_status': 'married',
        }
        user = User.objects.create(username='example-user-name')
        refresh = RefreshToken.for_user(user)
        self.assertEqual(Survey.objects.count(), 0)
        response = client.post(
            '/api/surveys',
            jsonDump(example_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Survey.objects.count(), 0)
