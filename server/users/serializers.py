from rest_framework import serializers
from django.contrib.auth import get_user_model
from teams.serializers import TeamSerializer

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    is_team_leader = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'ref', 'email',
            'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff',
            'date_joined', 'updated_at',
            'team', 'is_team_leader'
        ]
        read_only_fields = ['id', 'ref', 'date_joined', 'updated_at', 'full_name', 'team', 'is_team_leader']


class UserMeSerializer(UserSerializer):
    """Used for /me/ endpoint"""
    pass