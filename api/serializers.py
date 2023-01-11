from django.contrib.auth.models import User, Group
from api.models import Survey, SurveyResult, DataEntry
from rest_framework import serializers
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'


class SurveyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResult
        fields = '__all__'


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
            'idle_time',
        ]
        list_serializer_class = BulkListSerializer


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']