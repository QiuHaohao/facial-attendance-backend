from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.


class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def testSignUp_success(self):
        username, password = 'testuser', 'password'
        self.client.post(reverse('signup'),
                         {'username': username, 'password': password},
                         content_type="application/json")
        self.assertTrue(User.objects.filter(username=username).exists())
