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

        response = self.client.post(reverse('signup'),
                         {'username': username, 'password': password},
                         content_type="application/json")
        self.assertEqual(response.status_code, 400)


class CurrentUserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpassword')
        self.client.login(username='admin', password='adminpassword')

    def test_current_user(self):
        response = self.client.get(reverse('current_user').format(self.user.id), follow=True)
        self.assertEqual(response.status_code, 200)
