from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from api.models import StudyParticipant, SurveyResult, Survey, DataEntry


class StudyParticipantInline(admin.StackedInline):
    model = StudyParticipant
    can_delete = False

class SurveyInline(admin.StackedInline):
    model = Survey
    can_delete = False


class StudyParticipantAdmin(admin.ModelAdmin):
    filter_horizontal = ("surveys",)
    fields = (
        "surveys",
        "token",
        "phone_number",
        "confirmed_phone_number",
        "approved",
        "device_serial_number",
    )
    readonly_fields = (
        "phone_number",
        "token",
    )
    list_display = (
        "active_survey",
        "token",
        "phone_number",
        "confirmed_phone_number",
        "approved",
    )

    def identifier(self, obj):
        return obj.token[-10:]

    def active_survey(self, obj):
        return obj.surveys.first()


class SurveyAdmin(admin.ModelAdmin):
    filter_horizontal = ("participants",)
    fields = (
        "table_key",
        "created_at",
        "name",
        "slug",
        "participants",
    )
    readonly_fields = (
        "table_key",
        "created_at",
    )
    list_display = (
        "id",
        "name",
        "table_key",
        "created_at",
    )

    def identifier(self, obj):
        return obj.name or obj.table_key


class SurveyResultAdmin(admin.ModelAdmin):
    readonly_fields = (
      "hispanic_origin",
      "survey",
      "token",
      "computer_use",
      "household_computers",
      "household_members",
      "computer_difficulty_level",
      "solve_computer_problems_level",
      "handle_computer_problems_level",
      "computer_acting_up_level",
      "complex_computer_level",
      "internet_access",
      "race",
    )
    list_display = (
      "identifier",
      "hispanic_origin",
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
    readonly_fields = (
      "survey",
      "token",
      "identifier",
      "application_name",
      "tab_name",
      "url",
      "internet_connection",
      "timestamp",
      "idle_time",
    )
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
