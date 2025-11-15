from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User

class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@test.com", password="pass123")

    def test_login_success(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            "email": "test@test.com",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_login_fail(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            "email": "test@test.com",
            "password": "wrong"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        login = self.client.post(reverse('token_obtain_pair'), {
            "email": "test@test.com",
            "password": "pass123"
        })
        refresh = login.data['refresh']
        response = self.client.post(reverse('token_refresh'), {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout(self):
        login = self.client.post(reverse('token_obtain_pair'), {
            "email": "test@test.com",
            "password": "pass123"
        })
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + login.data['access'])
        response = self.client.post(reverse('token_blacklist'), {"refresh": login.data['refresh']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)