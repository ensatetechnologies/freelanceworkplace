"""
Serializers for proposals app.
"""
from rest_framework import serializers
from apps.accounts.serializers import PublicUserSerializer
from apps.projects.serializers import ProjectListSerializer
from .models import Proposal, ProposalAttachment


class ProposalAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ProposalAttachment model."""
    
    class Meta:
        model = ProposalAttachment
        fields = ['id', 'file', 'filename', 'description', 'created_at']
        read_only_fields = ['id', 'filename', 'created_at']


class ProposalListSerializer(serializers.ModelSerializer):
    """Serializer for Proposal list view."""
    freelancer = PublicUserSerializer(read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'id', 'project', 'project_title', 'freelancer', 'bid_amount',
            'estimated_duration', 'status', 'is_viewed', 'created_at'
        ]


class ProposalDetailSerializer(serializers.ModelSerializer):
    """Serializer for Proposal detail view."""
    freelancer = PublicUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    attachments = ProposalAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'id', 'project', 'freelancer', 'cover_letter', 'bid_amount',
            'estimated_duration', 'status', 'is_viewed', 'viewed_at',
            'attachments', 'created_at', 'updated_at'
        ]


class ProposalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating proposals."""
    
    class Meta:
        model = Proposal
        fields = ['project', 'cover_letter', 'bid_amount', 'estimated_duration']
    
    def validate_project(self, value):
        if value.status != 'open':
            raise serializers.ValidationError('This project is not accepting proposals.')
        
        user = self.context['request'].user
        if Proposal.objects.filter(project=value, freelancer=user).exists():
            raise serializers.ValidationError('You have already submitted a proposal for this project.')
        
        return value
    
    def create(self, validated_data):
        validated_data['freelancer'] = self.context['request'].user
        proposal = super().create(validated_data)
        
        # Update project proposals count
        proposal.project.proposals_count += 1
        proposal.project.save(update_fields=['proposals_count'])
        
        return proposal
