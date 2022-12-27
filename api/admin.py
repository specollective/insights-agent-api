from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from api.models import StudyParticipant, SurveyResult, Survey, DataEntry


class StudyParticipantInline(admin.StackedInline):
    model = StudyParticipant
    can_delete = False


class StudyParticipantAdmin(admin.ModelAdmin):
    list_display = (
      "token",
      "phone_number",
      "confirmed_phone_number",
    )

    def identifier(self, obj):
        return obj.token[-10:]


class SurveyAdmin(admin.ModelAdmin):
    fields = ('name', 'participants')

    list_display = (
      "id",
      "name",
      "table_key",
      "created_at",
    )

    def identifier(self, obj):
        return obj.table_key


class SurveyResultAdmin(admin.ModelAdmin):
    list_display = (
      "identifier",
      "computer_use",
      "household_computers",
      "household_members",
      "computer_difficulty_level",
      "solve_computer_problems_level",
      "handle_computer_problems_level",
      "computer_acting_up_level",
      "complex_computer_level",
      "internet_access",
      "race"
    )

    def identifier(self, obj):
        return obj.token[-10:]


class DataEntryAdmin(admin.ModelAdmin):
    list_display = (
      "identifier",
      "application_name",
      "tab_name",
      "url",
      "internet_connection",
      "timestamp",
    )

    def identifier(self, obj):
        return obj.token[-10:]


class UserAdmin(BaseUserAdmin):
    inlines = (StudyParticipantInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyResult, SurveyResultAdmin)
admin.site.register(DataEntry, DataEntryAdmin)
admin.site.register(StudyParticipant, StudyParticipantAdmin)
