import os
import uuid
from json import loads as loadJson
from cryptography.fernet import Fernet

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import StudyParticipant, Survey, DataEntry
from api.serializers import UserSerializer, GroupSerializer, SurveySerializer
from api.services import SmsClient
from api.services import SmsClient, OtpClient

from api.serializers import (
    DataEntrySerializer,
    GroupSerializer,
    SurveySerializer,
    UserSerializer,
)

from api.utils import (
    check_access_code_response_data,
    create_magic_link,
    create_study_participant,
    create_survey_token,
    find_study_participant_by_token,
    get_tokens_for_user,
    is_phone_number_taken,
)

User = get_user_model()
DEBUG = os.getenv('DEBUG', 'False') == 'True'
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'False') == 'True'
DEV_COOKIE_DOMAIN = 'localhost'
PROD_COOKIE_DOMAIN = '.specollective.org'

if DEVELOPMENT_MODE:
    AUTH_COOKIE_DOMAIN = DEV_COOKIE_DOMAIN
else:
    AUTH_COOKIE_DOMAIN = PROD_COOKIE_DOMAIN



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class DataEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows data entries to be created.
    """
    queryset = DataEntry.objects.all()
    serializer_class = DataEntrySerializer
    # TODO: Apply permissions
    permission_classes = []
    http_method_names = ['post']


@api_view(['POST'])
def send_ping(request):
    """
    API endpoint to test sending sms message via API
    """
    data = loadJson(request.body.decode("utf-8"))

    try:
        sms_client = SmsClient()
        sms_client.send_sms(data['phone_number'])
        return Response({"message": "success"}, status=200)
    except Exception as ex:
        return Response({"message": "error"}, status=400)


# POST /api/send_magic_link
@api_view(['POST'])
def send_magic_link(request):
    """
    API endpoint sends a magic link to the user
    """
    data = loadJson(request.body.decode("utf-8"))

    try:
        sms_client = SmsClient()
        sms_client.send_sms(data['phone_number'])
        return Response({"message": "success"}, status=200)
    except Exception as ex:
        return Response({"message": "error"}, status=400)


# POST /api/send_access_code
@api_view(['POST'])
def send_access_code(request):
    """
    API endpoint sends a magic link to the user
    """
    # 1. Parse request parameters.
    data = loadJson(request.body.decode("utf-8"))
    full_name = data['full_name']
    phone_number = data['phone_number']
    study_participant = create_study_participant(full_name, phone_number)

    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    token = str(study_participant.token)
    magic_link = create_magic_link(token)

    try:
        sms_client = SmsClient()
        sms_client.send_sms_magic_link(phone_number, magic_link)
        return Response({"message": "success", "token": token}, status=200)
    except Exception as ex:
        return Response({"message": "sms failed to send"}, status=400)


# POST /api/check_access_code
@api_view(['POST'])
def check_access_code(request):
    """
    API endpoint checks one-time passcode
    """
    data = loadJson(request.body.decode("utf-8"))

    study_participant = find_study_participant_by_token(data['token'])
    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    otp_client = OtpClient()
    if otp_client.verify(data['otp']):
        study_participant.confirmed_phone_number = True
        study_participant.save()
        refresh = RefreshToken.for_user(study_participant.user)
        response_data = {
          "message": "success",
          "refresh_token": str(refresh),
          "access_token": str(refresh.access_token),
        }
        response = Response(response_data, status=200)
        cookie_max_age = 3600 * 24 * 14  # 14 days

        response.set_cookie(
            'access_token',
            value=response_data['access_token'],
            max_age=cookie_max_age,
            expires=None,
            httponly=True,
            samesite='None',
            domain=AUTH_COOKIE_DOMAIN,
            secure=True,
        )

        return response
    else:
        return Response({"message": "invalid access code"}, status=400)


# POST /resend_access_code
@api_view(['POST'])
def resend_access_code(request):
    """
    API endpoint sends a magic link to the user
    """
    # 1. Parse request parameters.
    data = loadJson(request.body.decode("utf-8"))
    phone_number = data['phone_number']

    try:
        study_participant = StudyParticipant.objects.get(
          phone_number=phone_number
        )
        otp_client = OtpClient()
        sms_client = SmsClient()
        otp = otp_client.generate()
        sms_client.send_sms_access_code(phone_number, otp)
        return Response({"message": "success"}, status=200)
    except Exception as ex:
        return Response({"message": "invalid credentials"}, status=400)


# GET /api/current_user
@api_view(['GET'])
def current_user(request):
    serializer = UserSerializer(request.user, context={"request": request})
    if request.user.username == "":
        return Response({"message": "error"}, status=400)
    return Response(serializer.data)


# DELETE /api/logout
@api_view(['DELETE'])
def logout(request):
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('access_token')
    return response


# POST /api/surveys
@api_view(['POST'])
def surveys(request):
    error_messages = None
    data = loadJson(request.body.decode("utf-8"))
    survey = Survey(
      token=request.user.username,
      age=data['age'],
      gender=data['gender'],
      marital_status=data['marital_status'],
      hispanic_origin=data['hispanic_origin'] == 'true',
      education_level=data['education_level'],
    )

    try:
        survey.full_clean()
    except ValidationError as e:
        error_messages = e.message_dict
        return Response(error_messages, status=400)

    survey.save()
    serializer = SurveySerializer(survey)

    # TODO : Refactor to use rest framework
    # serializer = SurveySerializer(data=request.data)
    # if serializer.is_valid():
    #   serializer.save()
    #   return Response(serializer.data, status=status.HTTP_201_CREATED)
    # else
    #   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_201_CREATED)
