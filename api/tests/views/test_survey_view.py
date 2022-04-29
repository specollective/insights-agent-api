import os
import uuid
from json import dumps as jsonDump

from unittest import mock
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from rest_framework import status

from api.models import StudyParticipant, DataEntry, Survey
from api.services import SmsClient, OtpClient
from rest_framework_simplejwt.tokens import RefreshToken


class SurveyAPI(TestCase):
    """ Test module for Survey API """

    # TODO: Add assertion for HTTP only auth
    def test_data_survey_post_request(self):
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
            '/api/surveys/',
            jsonDump(example_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['education_level'], 'college')
