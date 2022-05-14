from django.test import TestCase


class PageTests(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
