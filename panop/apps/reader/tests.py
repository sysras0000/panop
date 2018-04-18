from django.core.urlresolvers import reverse
from django.test import TestCase, Client

# Create your tests here.

class TestHomePage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_url_returns_200(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)