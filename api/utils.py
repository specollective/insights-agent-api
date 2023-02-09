import os
import uuid
import json

from rest_framework_simplejwt.tokens import RefreshToken
from cryptography.fernet import Fernet

from django.contrib.auth import get_user_model
from api.models import StudyParticipant
from api.services import OtpClient
from django.http import JsonResponse
from rest_framework import status

# NOTE: This file is a grab bag of functions that are used in multiple places. We should
# refactor this file to be more organized and to have a better name.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    study_participant = user.studyparticipant
    fernet = Fernet(os.getenv('SECRET_KEY').encode('utf-8'))
    survey_token = fernet.encrypt(study_participant.token.encode('utf-8'))

    return {
        'status': 'success',
        'username': user.username,
        'refresh': refresh,
        'access': refresh.access_token,
        'survey_token': survey_token.decode('utf-8'),
    }


def is_phone_number_taken(phone_number):
    return StudyParticipant.objects.filter(phone_number=phone_number).exists()


def create_study_participant(full_name, phone_number):
    User = get_user_model()
    user = User.objects.create(username=str(uuid.uuid4()))

    user.password = str(uuid.uuid4())
    user.save()

    user.studyparticipant.full_name = full_name
    user.studyparticipant.phone_number = phone_number
    user.studyparticipant.save()

    return user.studyparticipant


def find_study_participant_by_token(token):
    try:
        return StudyParticipant.objects.get(token=token)
    except StudyParticipant.DoesNotExist:
        return None


def create_magic_link(token):
    otp_client = OtpClient()
    otp = otp_client.generate()
    base_url = os.getenv('CLIENT_URL')
    return f"{base_url}/confirmation/{otp}/{token}"


def create_survey_token(token):
    fernet = Fernet(os.getenv('SECRET_KEY').encode('utf-8'))
    return fernet.encrypt(token.encode('utf-8')).decode('utf-8')


def check_access_code_response_data(study_participant):
    survey_token = create_survey_token(study_participant.token)
    refresh = RefreshToken.for_user(study_participant.user)
    string_token = str(refresh.access_token)

    return {
        'message': 'success',
        'refresh_token': str(refresh),
        'access_token': string_token,
        'survey_token': survey_token,
    }


def desktop_client_response(data, status_code=status.HTTP_200_OK):
    """
    Formats the response from the client to be returned to the user.
    """
    response = JsonResponse(data, status=status_code)

    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

    return response


def parse_request_data(request):
    """
    Parse the request body as JSON.
    """
    try:
        return json.loads(request.body.decode('utf-8'))
    except ValueError:
        return {}