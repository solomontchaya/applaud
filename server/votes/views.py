from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiResponse

from votes.models import Vote
from votes.serializers import VoteCreateSerializer, VoteSerializer

@extend_schema(tags=['Votes'])
class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.select_related('project', 'voter', 'project__category').all()
    lookup_field = 'ref'
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VoteCreateSerializer
        return VoteSerializer

    @extend_schema(
        summary="Cast a vote (overall or category)",
        responses={
            201: VoteSerializer,
            400: OpenApiResponse(description="Already voted / invalid")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.save()
        return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="List all votes (admin only)")
    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Admin only."}, status=403)
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get user's votes")
    @action(detail=False, methods=['get'])
    def my_votes(self, request):
        votes = Vote.objects.filter(voter=request.user)
        serializer = VoteSerializer(votes, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Vote leaderboard")
    @action(detail=False, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request):
        # Top projects by total votes
        top_projects = (
            Vote.objects.values('project__ref', 'project__title')
            .annotate(total=Count('id'))
            .order_by('-total')[:10]
        )
        return Response(top_projects)