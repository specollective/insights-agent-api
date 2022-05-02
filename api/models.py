from phonenumber_field.modelfields import PhoneNumberField
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
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
    """Represents an indiviudal survey filled out by study participant."""

    age = models.PositiveIntegerField()
    education_level = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    hispanic_origin = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=100)
    token = models.CharField(max_length=200, blank=False, unique=True)

    def __str__(self):
        return self.token[-20:]


class DataEntry(models.Model):
    """Represents a single activity data point."""

    application_name = models.CharField(max_length=200)
    tab_name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    timestamp = models.DateTimeField()
    token = models.CharField(max_length=200, blank=True, unique=True)

    class Meta:
        verbose_name_plural = "Data Entries"


@receiver(post_save, sender=User)
def create_study_participant(sender, instance, created, **kwargs):
    if created:
        StudyParticipant.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_study_participant(sender, instance, **kwargs):
    instance.studyparticipant.save()
