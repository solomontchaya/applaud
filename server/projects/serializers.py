from rest_framework import serializers
from .models import Project
from categories.serializers import Category, CategorySerializer
from teams.serializers import TeamSerializer

class ProjectSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    team = TeamSerializer(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    overall_votes = serializers.IntegerField(read_only=True)
    category_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'ref', 'team', 'category', 'category_id',
            'name', 'summary', 'description', 'image',
            'created_at', 'updated_at',
            'total_votes', 'overall_votes', 'category_votes'
        ]
        read_only_fields = ['ref', 'team', 'created_at', 'updated_at', 'total_votes', 'overall_votes', 'category_votes']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            team = request.user.team_member.team  # Assuming user has one team; adjust as needed
            if Project.objects.filter(team=team).exists():
                raise serializers.ValidationError("Your team already has a project.")
            attrs['team'] = team
        return attrs

    def validate_name(self, value):
        return value.strip().name()