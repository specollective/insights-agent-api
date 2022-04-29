from unittest import mock
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


# class UserTest(TestCase):
#     """
#     Test module for user model
#     """
#
#     def test_study_participant_phone_number_presence_validation(self):
#         user1 = User.objects.create(username='example username')
#
#         try:
#             user2 = User.objects.create(username='example username')
#         except IntegrityError as e:
#             self.assertEqual(
#                 str(e.__cause__),
#                 "UNIQUE constraint failed: auth_user.username",
#              )
