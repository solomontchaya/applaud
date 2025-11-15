from rest_framework import serializers
from .models import Vote
from projects.serializers import ProjectSerializer

class VoteCreateSerializer(serializers.ModelSerializer):
    project_ref = serializers.UUIDField(write_only=True)
    is_overall = serializers.BooleanField()

    class Meta:
        model = Vote
        fields = ['project_ref', 'is_overall']
        extra_kwargs = {'is_overall': {'required': True}}

    def validate_project_ref(self, value):
        from projects.models import Project
        try:
            project = Project.objects.get(ref=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found.")
        return project

    def create(self, validated_data):
        project = validated_data.pop('project_ref')
        vote = Vote.objects.create(voter=self.context['request'].user, project=project, **validated_data)
        return vote


class VoteSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    voter_email = serializers.CharField(source='voter.email', read_only=True)

    class Meta:
        model = Vote
        fields = [
            'id', 'ref', 'voter_email', 'project',
            'is_overall', 'created_at', 'updated_at'
        ]
        read_only_fields = fields