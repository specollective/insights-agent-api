# Python standard library dependencies
import os
from json import loads as loadJson
# Django dependencies
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Django REST Framework dependencies
from rest_framework import permissions, generics, status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# Application dependencies
from api.models import StudyParticipant, Survey, SurveyResult, DataEntry
from api.services import SmsClient
from api.services import SmsClient, OtpClient
from api.serializers import (
    DataEntrySerializer,
    GroupSerializer,
    SurveySerializer,
    SurveyResultSerializer,
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
from rest_framework_bulk import (
  BulkListSerializer,
  BulkModelViewSet,
  ListBulkCreateUpdateDestroyAPIView,
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
    warning_msg = ""
    # 2. Create study particpant
    if StudyParticipant.objects.filter(phone_number=phone_number).exists():
        study_participant = StudyParticipant.objects.get(phone_number=phone_number)
        warning_msg = 'It looks like you have already signed up for this study with this phone number. Please follow the instructions given via text message. If you have not received a text message, please email tech4all@buildJUSTLY.org'
    else: 
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
        if warning_msg:
            return Response({"message": "success", "token": token, "error": warning_msg}, status=200)
        else: 
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
        login(request, study_participant.user)

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
        response = JsonResponse({
            "message": "success",
            "token": str(study_participant.token),
        }, status=200)

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

# Handles confirmation of access code for a study participant login
# from the desktop app.
#
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

        surveys = Survey.objects.filter(
            participants__id=study_participant.id,
        )

        # TODO: Handle multiple surveys
        survey = surveys[0]

        # 6. Build base JSON response object.
        response = JsonResponse({
          "message": "success",
          "survey_id": survey.id,
          "table_key": survey.table_key,
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


# DELETE /api/logout
@api_view(['DELETE'])
def logout(request):
    """
    API endpoint to logout a current user
    """
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('access_token')
    return response


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


# POST /api/survey_results
@api_view(['POST'])
def survey_results(request):
    """
    API endpoint to submit a survey result
    """
    error_messages = None
    data = loadJson(request.body.decode("utf-8"))

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
