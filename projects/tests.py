from django.test import TestCase, Client
from .models import Project
from rest_framework import status


# class ProjectModelTest(TestCase):
#     """ Test module for Project model """
#
#     def setUp(self):
#         Project.objects.create(title='Title #1', description='Description #1')
#         Project.objects.create(title='Title #2', description='Description #2')
#
#     def test_project_attributes(self):
#         project1 = Project.objects.get(title='Title #1')
#         project2 = Project.objects.get(title='Title #2')
#         self.assertEqual(project1.description, "Description #1")
#         self.assertEqual(project2.description, "Description #2")
#
# class ProjectAPITest(TestCase):
#     """ Test module for Project model """
#
#     def setUp(self):
#         Project.objects.create(title='Title #1', description='Description #1')
#         Project.objects.create(title='Title #2', description='Description #2')
#
#     def test_project_get_request(self):
#         client = Client()
#         response = client.post(
#             '/projects/',
#             '{"title": "Example title", "description": "Example description"}',
#             content_type="application/json"
#         )
#         json = response.json()
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(json['data']['title'], 'Example title')
