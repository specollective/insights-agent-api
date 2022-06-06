from django.contrib.auth.models import User, Group
from api.models import Survey, DataEntry
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Survey
        fields = [
            'token',
            'age',
            'gender',
            'hispanic_origin',
            'education_level',
        ]


class DataEntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataEntry
        fields = [
            'token',
            'application_name',
            'tab_name',
            'url',
            'timestamp',
            'internet_connection',
        ]
