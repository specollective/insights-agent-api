from django.contrib.auth.models import Group
from .models import StudyParticipant
from rest_framework import serializers


class StudyParticipantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StudyParticipant
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
