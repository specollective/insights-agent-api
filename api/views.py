from django.contrib.auth.models import Group
from .models import StudyParticipant
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from api.serializers import StudyParticipantSerializer, GroupSerializer
from django.http import JsonResponse
from api.services import SmsClient
from json import loads as loadJson


class StudyParticipantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = StudyParticipant.objects.all().order_by('-date_joined')
    serializer_class = StudyParticipantSerializer

    # NOTE: Implementation was adapted from StackOverflow https://stackoverflow.com/questions/25283797
    def get_permissions(self):
        if self.action == 'create':
            self.permissions_classes = [permissions.AllowAny]
        else:
            self.permissions_classes = [permissions.IsAuthenticated]

        return super(StudyParticipantViewSet, self).get_permissions()

# TODO: Determine if we need th
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [permissions.IsAuthenticated]


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
