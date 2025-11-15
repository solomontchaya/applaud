from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from teams.models import Team, TeamMember
from categories.models import Category
from projects.models import Project
from votes.models import Vote

class VoteAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="voter@test.com", password="pass")
        self.team = Team.objects.create(name="Team A")
        TeamMember.objects.create(team=self.team, user=self.user, role='admin')
        self.category = Category.objects.create(name="AI")
        self.project = Project.objects.create(
            team=self.team, category=self.category,
            title="AI Bot", summary="Smart", description="..."
        )
        self.client.force_authenticate(user=self.user)

    def test_cast_overall_vote(self):
        data = {"project_ref": self.project.ref, "is_overall": True}
        response = self.client.post(reverse('vote-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_vote_twice_overall(self):
        Vote.objects.create(voter=self.user, project=self.project, is_overall=True)
        data = {"project_ref": self.project.ref, "is_overall": True}
        response = self.client.post(reverse('vote-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_vote_twice_in_category(self):
        Vote.objects.create(voter=self.user, project=self.project, is_overall=False)
        data = {"project_ref": self.project.ref, "is_overall": False}
        response = self.client.post(reverse('vote-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_category_vote_requires_category(self):
        self.project.category = None
        self.project.save()
        data = {"project_ref": self.project.ref, "is_overall": False}
        response = self.client.post(reverse('vote-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)