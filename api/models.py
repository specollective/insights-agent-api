import uuid

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

#######################################################
# Study Participant
#######################################################

class StudyParticipant(models.Model):
    approved = models.BooleanField(default=False)
    confirmed_phone_number = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=100)
    token = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_study_participant(sender, instance, created, **kwargs):
    if created:
        StudyParticipant.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_study_participant(sender, instance, **kwargs):
    instance.studyparticipant.save()

#######################################################
# Survey
#######################################################

class Survey(models.Model):
    age = models.PositiveIntegerField()
    education_level = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    hispanic_origin = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=100)
    token = models.CharField(max_length=200, blank=True, unique=True)

    def __str__(self):
        return self.token[-20:]


#######################################################
# DataEntry
#######################################################

class DataEntry(models.Model):
    application_name = models.CharField(max_length=200)
    tab_name = models.CharField(max_length=200)
    url = models.URLField(max_length = 200)
    timestamp = models.DateTimeField()
    token = models.CharField(max_length=200, blank=True, unique=True)
