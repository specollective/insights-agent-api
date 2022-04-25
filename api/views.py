from json import loads as loadJson
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view

from api.services import SmsClient
from api.serializers import UserSerializer, GroupSerializer, SurveySerializer, DataEntrySerializer
from api.models import Survey, DataEntry


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
    API endpoint that allows survey to be viewed or edited.
    """
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = []


class DataEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows data entry to be viewed or edited.
    """
    queryset = DataEntry.objects.all()
    serializer_class = DataEntrySerializer
    permission_classes = []


@api_view(['POST'])
def send_magic_link(request):
    """
    API endpoint sends a magic link to the user
    """
    data = loadJson(request.body.decode("utf-8"))

    try:
        sms_client = SmsClient()
        response = sms_client.send_sms(data['phone_number'])
        return JsonResponse({ "message": "success" }, status=200)
    except:
        return JsonResponse({ "message": "error" }, status=400)
