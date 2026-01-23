"""
Serializers for accounts app.
"""
from rest_framework import serializers
from .models import User, FreelancerProfile, ClientProfile, Skill


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model."""
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug', 'category']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    avatar_url = serializers.CharField(source='get_avatar_url', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'avatar_url', 'phone', 'is_verified',
            'is_profile_complete', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'created_at']


class FreelancerProfileSerializer(serializers.ModelSerializer):
    """Serializer for FreelancerProfile model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FreelancerProfile
        fields = [
            'id', 'user', 'title', 'bio', 'hourly_rate', 'skills',
            'experience_years', 'portfolio_url', 'github_url', 'linkedin_url',
            'availability', 'total_earnings', 'avg_rating', 'total_reviews',
            'completed_projects', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_earnings', 'avg_rating', 'total_reviews',
            'completed_projects', 'created_at', 'updated_at'
        ]


class ClientProfileSerializer(serializers.ModelSerializer):
    """Serializer for ClientProfile model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'company_name', 'company_website', 'industry',
            'company_size', 'total_spent', 'avg_rating', 'total_reviews',
            'projects_posted', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_spent', 'avg_rating', 'total_reviews',
            'projects_posted', 'created_at', 'updated_at'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PublicUserSerializer(serializers.ModelSerializer):
    """Serializer for public user information."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    avatar_url = serializers.CharField(source='get_avatar_url', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'avatar_url', 'role']
