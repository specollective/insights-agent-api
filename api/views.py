# Python standard library dependencies
import os
# Django dependencies
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Django REST Framework dependencies
from rest_framework import permissions, generics, status, viewsets
from rest_framework_bulk import BulkModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
# Models
from api.models import StudyParticipant, Survey, SurveyResult, DataEntry
# Services
from api.services import SmsClient, OtpClient
# Serializers
from api.serializers import (
    DataEntrySerializer,
    GroupSerializer,
    SurveyResultSerializer,
    SurveySerializer,
    UserSerializer,
)
# Utilities
from api.utils import (
    create_magic_link,
    create_study_participant,
    create_survey_token,
    desktop_client_response,
    find_study_participant_by_token,
    parse_request_data,
)


# Variable initialization
User = get_user_model()
DEBUG = os.getenv('DEBUG', 'False') == 'True'
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
    permission_classes = []


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class DataEntryViewSet(BulkModelViewSet):
    """
    API endpoint that allows data entries to be created.
    """
    queryset = DataEntry.objects.all()
    serializer_class = DataEntrySerializer
    # NOTE: We skip authentication for posting new data entries.
    permission_classes = []
    http_method_names = ['post']


class ListSurvey(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [ permissions.IsAuthenticatedOrReadOnly]


class DetailSurvey(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

##################################################
# Serial Number API endpoints
##################################################

@csrf_exempt
def confirm_serial_number(request):
    """
    API endpoint confirming serial number is in db and returning token, and survey_id, table_key 
    """
    data = parse_request_data(request)
    device_serial_number = data['serial_number']

    try:
         # Find study participant by serial number
        study_participant = StudyParticipant.objects.get(device_serial_number=device_serial_number)
        survey = study_participant.active_survey()

        # Build base JSON response object
        response_data = {
          "message": "success",
          "token": str(study_participant.token),
          "survey_id": survey.id,
          "table_key": survey.table_key,
        }

        return desktop_client_response(response_data, status.HTTP_200_OK)
    except:
        response_data = { "message": 'invalid credentials' }
        return desktop_client_response(response_data, status.HTTP_400_BAD_REQUEST)

##################################################
# Magic Link API endpoints
##################################################

# POST /api/send_magic_link
@api_view(['POST'])
def send_magic_link(request):
    """
    API endpoint sends a magic link to the user
    """
    data = parse_request_data(request)
    full_name = data['full_name']
    phone_number = data['phone_number']
    warning_msg = ""

    # Create study particpant
    if StudyParticipant.objects.filter(phone_number=phone_number).exists():
        study_participant = StudyParticipant.objects.get(phone_number=phone_number)
        warning_msg = 'It looks like you have already signed up for this study with this phone number. Please follow the instructions given via text message. If you have not received a text message, please email tech4all@buildJUSTLY.org'
    else: 
        study_participant = create_study_participant(full_name, phone_number)
    
    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    # Generate magic link
    token = str(study_participant.token)
    magic_link = create_magic_link(token)

    # Send magic link
    try:
        sms_client = SmsClient()
        sms_client.send_sms_magic_link(phone_number, magic_link)
        if warning_msg:
            return Response({"message": "success", "token": token, "error": warning_msg}, status=status.HTTP_200_OK)
        else: 
            return Response({"message": "success", "token": token}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"message": "sms failed to send"}, status=400)


# POST /api/confirm_magic_link
@api_view(['POST'])
def confirm_magic_link(request):
    """
    API endpoint checks magic link code
    """
    data = parse_request_data(request)

    # Find the study particpant by their token
    study_participant = find_study_participant_by_token(data['token'])
    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    # Verify the one-time password
    otp_client = OtpClient()
    if otp_client.verify(data['otp']):
        # Set confirmed phone number to true and save record.
        study_participant.confirmed_phone_number = True
        study_participant.save()
        login(request, study_participant.user)

        # Generate JWT access tokens
        refresh = RefreshToken.for_user(study_participant.user)
        
        response_data = {
            "message": "success",
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }

        # 6. Create base JSON response
        response = Response(response_data, status=status.HTTP_200_OK)

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


##################################################
# User API endpoints
##################################################

# GET /api/current_user
@api_view(['GET'])
def current_user(request):
    """
    API endpoint to fetch a current user
    """
    serializer = UserSerializer(
        request.user,
        context={"request": request}
    )

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


##################################################
# Survey results API endpoints
##################################################

# Handles creation of survey results.
# 
# POST /api/survey_results
@api_view(['POST'])
def survey_results(request):
    """
    API endpoint to submit a survey result
    """
    error_messages = None
    data = parse_request_data(request)

    try:
        survey = Survey.objects.get(slug=data['survey_id'])
        participant = StudyParticipant.objects.get(user=request.user)
        survey_token = create_survey_token(participant.token)
    except ValidationError as e:
        error_messages = e.message_dict
        return Response(error_messages, status=400)

    survey_result = SurveyResult(
        token=survey_token,
        survey_id=survey.id,
        computer_use=data['computer_use'],
        hispanic_origin=data['hispanic_origin'] == 'true',
        household_computers=data['household_computers'],
        household_members=data['household_members'],
        internet_access=data['internet_access'],
        computer_difficulty_level=data['computer_difficulty_level'],
        solve_computer_problems_level=data['solve_computer_problems_level'],
        handle_computer_problems_level=data['handle_computer_problems_level'],
        computer_acting_up_level=data['computer_acting_up_level'],
        complex_computer_level=data['complex_computer_level'],
        race=data['race'],
    )

    try:
        survey_result.full_clean()
        survey.participants.add(participant)
        survey_result.save()
    except ValidationError as e:
        error_messages = e.message_dict
        return Response(error_messages, status=400)

    serializer = SurveyResultSerializer(survey_result)

    return Response(serializer.data, status=status.HTTP_201_CREATED)

##################################################
# Access code API endpoints
##################################################

# Handles SMS access code requests from the desktop app
# 
# POST /api/send_access_code
@csrf_exempt
def send_access_code(request):
    """
    API endpoint confirms presence of study participant by phone number, sends code, returns token
    """
    data = parse_request_data(request)
    phone_number = data['phone_number']

    try:
        # Find study participant by phone number
        study_participant = StudyParticipant.objects.get(phone_number=phone_number)

        # Generate one-time passcode
        otp_client = OtpClient()
        otp = otp_client.generate()

        # Send OTP via SMS
        sms_client = SmsClient()
        sms_client.send_sms_access_code(phone_number, otp)
        
        # Build response data object
        response_data = {
            "message": "success",
            "token": str(study_participant.token),
        }
        return desktop_client_response(response_data, status.HTTP_200_OK)
    except Exception as ex:
        return desktop_client_response({ "message": 'invalid credentials' }, status.HTTP_400_BAD_REQUEST)

# Handles confirmation of access code for a study participant login
# from the desktop app.
#
# POST /api/confirm_access_code
@csrf_exempt
def confirm_access_code(request):
    """
    API endpoint to confirm access code
    """
    # Parse request parameters.
    data = parse_request_data(request)
    access_code = data['access_code']

    study_participant = find_study_participant_by_token(data['token'])
    if study_participant is None:
        return desktop_client_response({ "message": "invalid credentials" }, status.HTTP_400_BAD_REQUEST)
    
    survey = study_participant.active_survey()
    if survey is None:
        return desktop_client_response({ "message": "invalid credentials" }, status.HTTP_400_BAD_REQUEST)

    # Verify one-time passcode
    otp_client = OtpClient()
    if otp_client.verify(access_code):
        response_data = {
            "message": "success",
            "survey_id": survey.id,
            "table_key": survey.table_key,
        }
        return desktop_client_response(response_data, status.HTTP_200_OK)
    else:
        response_data = { "message": 'invalid access code' }
        return desktop_client_response(response_data, status.HTTP_400_BAD_REQUEST)
