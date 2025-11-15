from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Project
from teams.models import Team
from categories.models import Category
from users.models import User

class ProjectAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@test.com", password="user123")
        self.leader = User.objects.create_user(email="leader@test.com", password="leader123")
        self.team = Team.objects.create(name="Team A", description="...")
        # Assume TeamMember creation: leader in team as leader, user in team as member
        self.category = Category.objects.create(name="Tech")
        self.project = Project.objects.create(
            team=self.team, category=self.category,
            title="Project X", summary="Summary", description="Desc"
        )
        self.client.force_authenticate(user=self.leader)  # Assume leader auth

    def test_list_projects(self):
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_project_as_leader(self):
        data = {
            "category_id": self.category.id,
            "title": "New Project",
            "summary": "Short summary",
            "description": "Full desc"
        }
        response = self.client.post(reverse('project-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)

    def test_create_duplicate_project_fails(self):
        # First create one
        self.test_create_project_as_leader()
        # Try again
        data = {"category_id": self.category.id, "title": "Another"}
        response = self.client.post(reverse('project-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_project_as_non_leader(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "Updated"}
        response = self.client.patch(reverse('project-detail', kwargs={'ref': self.project.ref}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)