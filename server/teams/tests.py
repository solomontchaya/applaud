from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Team, TeamMember
from users.models import User

class TeamAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email="a@test.com", password="pass")
        self.user2 = User.objects.create_user(email="b@test.com", password="pass")
        self.client.force_authenticate(user=self.user1)

    def test_create_team(self):
        data = {"name": "Alpha Squad", "description": "Best team"}
        response = self.client.post(reverse('team-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
        self.assertTrue(TeamMember.objects.filter(user=self.user1, role='admin').exists())

    def test_join_team(self):
        team = Team.objects.create(name="Beta")
        TeamMember.objects.create(team=team, user=self.user2, role='admin')
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(reverse('team-join', kwargs={'ref': team.ref}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(team.memberships.count(), 2)

    def test_leave_team(self):
        team = Team.objects.create(name="Gamma")
        TeamMember.objects.create(team=team, user=self.user1, role='member')
        response = self.client.post(reverse('team-leave', kwargs={'ref': team.ref}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamMember.objects.filter(user=self.user1).exists())