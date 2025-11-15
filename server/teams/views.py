from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from teams.models import Team, TeamMember
from teams.serializers import TeamSerializer, TeamCreateSerializer, TeamMemberSerializer


@extend_schema(tags=['Teams'])
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    lookup_field = 'ref'

    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        return TeamSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [IsAdminUser()]

    @extend_schema(
        summary="List all teams",
        responses={200: TeamSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new team (user becomes admin)",
        responses={201: TeamSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()

        # Auto-add creator as admin
        TeamMember.objects.create(
            team=team,
            user=request.user,
            role='admin'
        )
        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Join a team (invite code or open join not implemented)",
        request=None,
        responses={200: TeamMemberSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, ref=None):
        team = self.get_object()
        if team.memberships.filter(user=request.user).exists():
            return Response({"error": "Already a member."}, status=status.HTTP_400_BAD_REQUEST)

        membership = TeamMember.objects.create(
            team=team,
            user=request.user,
            role='member'
        )
        return Response(TeamMemberSerializer(membership).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Leave team",
        responses={204: None}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, ref=None):
        team = self.get_object()
        membership = get_object_or_404(TeamMember, team=team, user=request.user)

        if membership.role == 'admin' and team.memberships.filter(role='admin').count() == 1:
            return Response({"error": "Admin cannot leave. Assign new admin first."}, status=400)

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Promote member to admin (current admin only)",
        request=TeamMemberSerializer
    )
    @action(detail=True, methods=['patch'], url_path='promote/(?P<user_id>[^/.]+)')
    def promote(self, request, ref=None, user_id=None):
        team = self.get_object()
        current_admin = team.memberships.filter(user=request.user, role='admin').exists()
        if not current_admin:
            return Response({"error": "Only admins can promote."}, status=403)

        member = get_object_or_404(TeamMember, team=team, user_id=user_id)
        member.role = 'admin'
        member.save()
        return Response(TeamMemberSerializer(member).data)