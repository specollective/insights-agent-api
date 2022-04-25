from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from api.models import StudyParticipant, Survey


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class StudyParticipantInline(admin.StackedInline):
    model = StudyParticipant
    can_delete = False
    verbose_name_plural = 'study participants'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (StudyParticipantInline,)


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


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Survey, SurveyAdmin)
