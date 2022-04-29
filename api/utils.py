import os
import uuid
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from cryptography.fernet import Fernet
from api.services import SmsClient, OtpClient
from api.models import Survey, DataEntry, StudyParticipant
from django.db import transaction


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
    if StudyParticipant.objects.filter(phone_number=phone_number).exists():
        return None

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
