import os
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from cryptography.fernet import Fernet
from api.services import SmsClient, OtpClient
from api.models import Survey, DataEntry, StudyParticipant


User = get_user_model()
otp_client = OtpClient()
sms_client = SmsClient()


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


def create_study_participant(username, phone_number):
    try:
        user = User.objects.create(username=username)
        user.studyparticipant.phone_number = phone_number
        user.studyparticipant.save()
        return user.studyparticipant
    except IntegrityError as e:
        print(e.__cause__)
        return None


def create_magic_link(study_participant):
    otp = otp_client.generate()
    token = str(study_participant.token)
    return f"http://localhost:3000/confirmation/{otp}/{token}"
