from json import dumps as jsonDump
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Survey


class SurveyAPI(TestCase):
    """ Test module for Survey API """
    def setUp(self):
        self.user = User.objects.create(username='example-user-name')
        self.participant = self.user.studyparticipant
        self.survey = Survey.objects.create()
        Survey.objects.create()
        Survey.objects.create()

    def test_survey_get_request(self):
        client = Client()
        response = client.get('/api/surveys')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 3)
    
    def test_survey_post_request(self):
        self.assertEqual(Survey.objects.count(), 3)
        client = Client()
        refresh = RefreshToken.for_user(self.user)
        response = client.post(
            '/api/surveys',
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id = response_data['id']
        self.assertIn(f"_{id}_", Survey.objects.get(pk=id).table_key)

    def test_survey_show_request(self):
        client = Client()
        response = client.get(f"/api/surveys/{self.survey.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['table_key'], Survey.objects.get(pk=self.survey.id).table_key)

    def test_survey_update_request(self):
        client = Client()
        request_data = {
            'participants': [self.participant.id],
        }

        refresh = RefreshToken.for_user(self.user)
        response = client.put(
            f"/api/surveys/{self.survey.id}/",
            jsonDump(request_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['participants'], [self.participant.id])

