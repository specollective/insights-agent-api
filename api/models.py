import random
import string
from phonenumber_field.modelfields import PhoneNumberField
from uuid import uuid4
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class StudyParticipant(models.Model):
    """Represents an indiviudal study participant."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=400)
    approved = models.BooleanField(default=False)
    confirmed_phone_number = models.BooleanField(default=False)
    phone_number = PhoneNumberField(blank=False)
    token = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        default=uuid4
    )

class Survey(models.Model):
    """Represents an indiviudal survey"""

    table_key = models.CharField(
        unique=True,
        max_length=63, 
        default=uuid4,
        editable=False,
        )

    participants = models.ManyToManyField(StudyParticipant)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SurveyResult(models.Model):
    """Represents an indiviudal survey result filled out by study participant."""

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, blank=False, null=True)
    participant = models.ForeignKey(StudyParticipant, on_delete=models.CASCADE, blank=False, null=True)    
    token = models.CharField(max_length=200, blank=False, unique=True)
    hispanic_origin = models.BooleanField(default=False, null=True)
    computer_use = models.TextField(blank=False, null=True)
    household_computers = models.IntegerField(blank=False, null=True)
    household_members = models.IntegerField(blank=False, null=True)
    internet_access = models.TextField(blank=False, null=True)
    technology_compentency_level = models.IntegerField(blank=False, null=True)

    def __str__(self):
        return self.token[-20:]


class DataEntry(models.Model):
    """Represents a single activity data point."""

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, blank=False, null=True)
    application_name = models.CharField(max_length=200)
    tab_name = models.CharField(max_length=200, blank=True)
    url = models.URLField(max_length=200, blank=True)
    timestamp = models.DateTimeField()
    token = models.CharField(max_length=200, blank=True)
    internet_connection = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "Data Entries"


@receiver(post_save, sender=Survey)
def set_uniq_table_key(sender, instance, created, **kwargs):
    # The table key must be updated to be an unique alphanumeric key to be used as a postgres table name in the data injestion service.
    if created:
        instance.update(key=f"_{instance.id}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=16))}")

@receiver(post_save, sender=User)
def create_study_participant(sender, instance, created, **kwargs):
    if created:
        StudyParticipant.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_study_participant(sender, instance, **kwargs):
#     instance.studyparticipant.save()
