"""
Serializers for projects app.
"""
from rest_framework import serializers
from apps.accounts.serializers import PublicUserSerializer
from .models import Project, Category, ProjectAttachment


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    project_count = serializers.IntegerField(source='get_project_count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'project_count']


class ProjectAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ProjectAttachment model."""
    
    class Meta:
        model = ProjectAttachment
        fields = ['id', 'file', 'filename', 'file_size', 'file_type', 'created_at']
        read_only_fields = ['id', 'filename', 'file_size', 'file_type', 'created_at']


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for Project list view."""
    client = PublicUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    budget_display = serializers.CharField(source='get_budget_display', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'client', 'category', 'budget_type',
            'budget_min', 'budget_max', 'budget_display', 'experience_level',
            'estimated_duration', 'status', 'proposals_count', 'views_count',
            'is_featured', 'is_urgent', 'created_at'
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for Project detail view."""
    client = PublicUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    attachments = ProjectAttachmentSerializer(many=True, read_only=True)
    budget_display = serializers.CharField(source='get_budget_display', read_only=True)
    skills_list = serializers.ListField(source='get_skills_list', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'client', 'category',
            'skills_required', 'skills_list', 'budget_type', 'budget_min',
            'budget_max', 'budget_display', 'experience_level', 'estimated_duration',
            'status', 'deadline', 'published_at', 'views_count', 'proposals_count',
            'is_featured', 'is_urgent', 'attachments', 'created_at', 'updated_at'
        ]


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating projects."""
    skills_input = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category', 'skills_input', 'budget_type',
            'budget_min', 'budget_max', 'experience_level', 'estimated_duration',
            'deadline', 'is_urgent'
        ]
    
    def validate(self, data):
        if data.get('budget_max', 0) < data.get('budget_min', 0):
            raise serializers.ValidationError({
                'budget_max': 'Maximum budget must be greater than minimum.'
            })
        return data
    
    def create(self, validated_data):
        skills_input = validated_data.pop('skills_input', '')
        if skills_input:
            validated_data['skills_required'] = [
                s.strip() for s in skills_input.split(',') if s.strip()
            ]
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)
