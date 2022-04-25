import os
from json import loads as loadJson
from cryptography.fernet import Fernet

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import StudyParticipant, Survey
from api.serializers import UserSerializer, GroupSerializer, SurveySerializer
from api.services import SmsClient, OtpClient
from api.models import Survey, DataEntry, StudyParticipant
from api.services import SmsClient
from api.serializers import (
    UserSerializer,
    GroupSerializer,
    SurveySerializer,
    DataEntrySerializer
)
from api.utils import (
    get_tokens_for_user,
    is_phone_number_taken,
    create_study_participant,
    create_magic_link,
)

User = get_user_model()
otp_client = OtpClient()
sms_client = SmsClient()

DEBUG = os.getenv("DEBUG", "False") == "True"
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

###############################################################
# REST Framework ModelViewSets
###############################################################


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


class SurveyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows surveys to be created.
    """
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']


class DataEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows data entries to be created.
    """
    queryset = DataEntry.objects.all()
    serializer_class = DataEntrySerializer
    # TODO: Apply permissions
    permission_classes = []
    http_method_names = ['post']


###############################################################
# Authentication API
###############################################################

# POST /api/send_magic_link
@api_view(['POST'])
def send_magic_link(request):
    """
    API endpoint sends a magic link to the user
    """
    data = loadJson(request.body.decode("utf-8"))

    try:
        sms_client.send_sms(data['phone_number'])
        return Response({"message": "success"}, status=200)
    except:
        return Response({"message": "error"}, status=400)


# POST /api/send_access_code
@api_view(['POST'])
def send_access_code(request):
    """
    API endpoint sends a magic link to the user
    """
    # 1. Parse request parameters.
    data = loadJson(request.body.decode("utf-8"))
    username = data['name']
    phone_number = data['phone_number']

    if is_phone_number_taken(phone_number):
        return Response({"message": "invalid credentials"}, status=400)

    study_participant = create_study_participant(username, phone_number)

    if study_participant is None:
        return Response({"message": "invalid credentials"}, status=400)

    magic_link = create_magic_link(study_participant)

    try:
        if DEVELOPMENT_MODE:
            print(magic_link)
        else:
            sms_client.send_sms_magic_link(phone_number, magic_link)

        return Response({
            "status": "success",
            "token": str(study_participant.token),
        }, status=200)
    except:
        return Response({"status": "error"}, status=400)


# POST /api/check_access_code
@api_view(['POST'])
def check_access_code(request):
    """
    API endpoint checks one-time passcode
    """
    data = loadJson(request.body.decode("utf-8"))

    try:
        study_participant = StudyParticipant.objects.get(token=data['token'])
    except StudyParticipant.DoesNotExist:
        return Response({
            "status": "error",
            "message:": "invalid credentials"
        }, status=400)

    otp_client = OtpClient()
    if otp_client.verify(data['otp']):
        try:
            study_participant.confirmed_phone_number = True
            study_participant.save()

            user = study_participant.user
            refresh = RefreshToken.for_user(user)
            fernet = Fernet(os.getenv('SECRET_KEY').encode('utf-8'))
            survey_token = fernet.encrypt(
                study_participant.token.encode('utf-8')
            )
            access_token = refresh.access_token
            string_token = str(access_token)

            response_data = {
                'status': 'success',
                'refresh': str(refresh),
                'access': string_token,
                'survey_token': survey_token.decode('utf-8'),
            }

            response = Response(response_data, status=200)
            cookie_max_age = 3600 * 24 * 14   # 14 days
            response.set_cookie(
                'access_token',
                string_token,
                max_age=cookie_max_age,
                httponly=True
            )

            return response
        except:
            return Response({
                "status": "error",
                "message:": "something went wrong"
            }, status=400)
    else:
        return Response({"status": "error"}, status=400)


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
        otp = otp_client.generate()
        token = str(study_participant.token)
        magic_link = f"http://localhost:3000/confirmation/{otp}/{token}"

        if DEVELOPMENT_MODE:
            print(magic_link)

        sms_client.send_sms_magic_link(data['phone_number'], otp)

        return Response({"status": "success", "token": token}, status=200)
    except:
        return Response({"status": "invalid credentials"}, status=400)


@api_view(['DELETE'])
def logout(request):
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('access_token')
    return response


# GET /api/current_user
@api_view(['GET'])
def current_user(request):
    serializer = UserSerializer(request.user, context={"request": request})
    if request.user.username == "":
        return Response({"status": "error"}, status=400)
    return Response(serializer.data)
