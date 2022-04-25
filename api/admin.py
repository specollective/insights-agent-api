from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from api.models import StudyParticipant, Survey, DataEntry


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
    list_display = (
      "identifier",
      "age",
      "gender",
      "education_level",
      "marital_status",
      "hispanic_origin",
    )

    def identifier(self, obj):
        return obj.token[-10:]


class DataEntryAdmin(admin.ModelAdmin):
    list_display = (
      "token",
      "application_name",
      "tab_name",
      "url",
      "timestamp",
    )

    def identifier(self, obj):
        return obj.token[-10:]


class UserAdmin(BaseUserAdmin):
    inlines = (StudyParticipantInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(DataEntry, DataEntryAdmin)
admin.site.register(StudyParticipant, StudyParticipantAdmin)
