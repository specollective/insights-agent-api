from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class StudyParticipant(AbstractUser):
    is_verified = models.BooleanField(default=False)
    phone_number = PhoneNumberField(blank=False, unique=True)
