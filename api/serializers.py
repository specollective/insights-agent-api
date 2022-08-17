from django.contrib.auth.models import User, Group
from api.models import Survey, DataEntry
from rest_framework import serializers
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer


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
            'computer_use',
            'household_members',
            'household_computers',
            'hispanic_origin',
            'technology_compentency_level',
            'internet_access',
        ]


class DataEntrySerializer(BulkSerializerMixin, serializers.ModelSerializer):
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
        list_serializer_class = BulkListSerializer
