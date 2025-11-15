from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User

class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email="admin@test.com", password="admin123")
        self.user = User.objects.create_user(email="user@test.com", password="user123", first_name="John")

    def test_register_user(self):
        data = {
            "email": "new@test.com",
            "password": "secure123",
            "first_name": "Jane",
            "last_name": "Doe"
        }
        response = self.client.post(reverse('user-register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_me_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('user-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], "user@test.com")

    def test_update_me(self):
        self.client.force_authenticate(user=self.user)
        data = {"first_name": "Johnny"}
        response = self.client.patch(reverse('user-me'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Johnny")

    def test_admin_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)