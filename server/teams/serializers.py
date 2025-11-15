from rest_framework import serializers
from teams.models import Team, TeamMember
from users.models import User
#from users.serializers import User, UserSerializer

class TeamMemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),   # ← real QuerySet
        write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = TeamMember
        fields = ['user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['joined_at']

class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(source='memberships', many=True, read_only=True)
    leader = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),   # ← real QuerySet
        write_only=True
    )
    member_count = serializers.IntegerField(read_only=True)
    project_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'ref', 'name', 'description',
            'created_at', 'updated_at',
            'member_count', 'project_count',
            'leader', 'members'
        ]
        read_only_fields = ['created_at', 'updated_at', 'member_count', 'project_count', 'leader']


class TeamCreateSerializer(serializers.ModelSerializer):
    """Used only for creating team (admin or first member)"""
    class Meta:
        model = Team
        fields = ['name', 'description']

    def validate_name(self, value):
        if Team.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A team with this name already exists.")
        return value.strip().name()