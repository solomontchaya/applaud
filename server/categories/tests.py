from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from categories.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

class CategoryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email="admin@test.com", password="admin123")
        self.user = User.objects.create_user(email="user@test.com", password="user123")

        self.category = Category.objects.create(
            name="Robotics", description="AI and hardware projects"
        )

    def test_list_categories_anonymous(self):
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_category_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Web Development", "description": "Full-stack web apps"}
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_category_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Mobile Apps"}
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_with_projects_fails(self):
        from projects.models import Project  # assuming Project exists
        Project.objects.create(team_id=1, category=self.category, name="Test", summary="...")
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(reverse('category-detail', kwargs={'id': self.category.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)