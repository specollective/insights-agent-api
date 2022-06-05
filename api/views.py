# Python standard library dependencies
import os
import uuid
from json import loads as loadJson
# Django dependencies
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Django REST Framework dependencies
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Application dependencies
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
    create_magic_link,
    create_study_participant,
    create_survey_token,
    find_study_participant_by_token,
    get_tokens_for_user,
    is_phone_number_taken,
)
# Variable initialization
User = get_user_model()
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'False') == 'True'
DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE', 'False') == 'True'
AUTH_COOKIE_DOMAIN = 'localhost' if DEVELOPMENT_MODE else '.specollective.org'

##################################################
# Django REST Framework API endpoints
##################################################

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
    http_method_names = ['post', 'get']

##################################################
# Authentication API endpoints
##################################################

# POST /api/send_magic_link
@api_view(['POST'])
def send_magic_link(request):
    """
    API endpoint sends a magic link to the user
    """
    # 1. Parse request parameters.
    data = loadJson(request.body.decode("utf-8"))
    full_name = data['full_name']
    phone_number = data['phone_number']

    # 2. Create study particpant
    study_participant = create_study_participant(full_name, phone_number)
    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    # 3. Generate magic link
    token = str(study_participant.token)
    magic_link = create_magic_link(token)

    # 4. Send magic link
    try:
        sms_client = SmsClient()
        sms_client.send_sms_magic_link(phone_number, magic_link)
        return Response({"message": "success", "token": token}, status=200)
    except Exception as ex:
        return Response({"message": "sms failed to send"}, status=400)


# POST /api/confirm_magic_link
@api_view(['POST'])
def confirm_magic_link(request):
    """
    API endpoint checks magic link code
    """
    # 1. Parse request parameters.
    data = loadJson(request.body.decode("utf-8"))

    # 2. Find the study particpant by their token
    study_participant = find_study_participant_by_token(data['token'])
    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    # 3. Verify the one-time password
    otp_client = OtpClient()
    if otp_client.verify(data['otp']):
        # 4. Set confirmed phone number to true and save record.
        study_participant.confirmed_phone_number = True
        study_participant.save()

        # 5. Generate JWT access tokens
        refresh = RefreshToken.for_user(study_participant.user)
        response_data = {
          "message": "success",
          "refresh_token": str(refresh),
          "access_token": str(refresh.access_token),
        }

        # 6. Create base JSON response
        response = Response(response_data, status=200)

        # 7. Set HTTP only cookie
        response.set_cookie(
            'access_token',
            value=response_data['access_token'],
            max_age=(3600 * 24 * 14),
            expires=None,
            httponly=True,
            samesite='None',
            domain=AUTH_COOKIE_DOMAIN,
            secure=True,
        )

        return response
    else:
        return Response({"message": "invalid access code"}, status=400)


# POST /api/send_access_code
@csrf_exempt
def send_access_code(request):
    """
    API endpoint sends a magic link to the user
    """
    # 1. Parse request parameters.
    data = loadJson(request.body.decode("utf-8"))
    phone_number = data['phone_number']

    try:
        # 2. Find study participant by phone number
        study_participant = StudyParticipant.objects.get(
          phone_number=phone_number
        )

        # 3. Generate one-time passcode
        otp_client = OtpClient()
        otp = otp_client.generate()

        # 4. Sent OTP via SMS
        sms_client = SmsClient()
        sms_client.send_sms_access_code(phone_number, otp)

        # 5. Build base JSON response object
        response = JsonResponse({ "message": "success" }, status=200)

        # 6. Set headers for CORS
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

        return response
    except Exception as ex:
        response = JsonResponse({ "message": 'invalid credentials' }, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

        return response


# POST /api/confirm_access_code
@csrf_exempt
def confirm_access_code(request):
    """
    API endpoint to confirm access code
    """
    # 1. Parse request parameters.
    data = loadJson(request.body.decode("utf-8"))
    access_code = data['access_code']

    jwtAuth = JWTAuthentication()

    # 2. Find the study particpant by their token
    study_participant = find_study_participant_by_token(data['token'])
    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    # 3. Verify one-time passcode
    otp_client = OtpClient()
    if otp_client.verify(access_code):
        # 5. Create survey token
        survey_token = create_survey_token(study_participant.token)

        # 6. Build base JSON response object.
        response = JsonResponse({
          "message": "success",
          "survey_token": survey_token,
        })

        # 7. Set headers for CORS
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

        # 8. Return response object.
        return response
    else:
        return JsonResponse({"message": "invalid access code"}, status=400)


# GET /api/current_user
@api_view(['GET'])
def current_user(request):
    """
    API endpoint to fetch a current user
    """
    serializer = UserSerializer(request.user, context={"request": request})
    if request.user.username == "":
        return Response({"message": "error"}, status=400)
    return Response(serializer.data)


# DELETE /api/logout
@api_view(['DELETE'])
def logout(request):
    """
    API endpoint to logout a current user
    """
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('access_token')
    return response


# POST /api/surveys
@api_view(['POST'])
def surveys(request):
    """
    API endpoint to submit a survey
    """
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
