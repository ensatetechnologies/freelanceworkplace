"""
Serializers for contracts app.
"""
from rest_framework import serializers
from apps.accounts.serializers import PublicUserSerializer
from .models import Contract, Milestone, Deliverable


class DeliverableSerializer(serializers.ModelSerializer):
    """Serializer for Deliverable model."""
    
    class Meta:
        model = Deliverable
        fields = ['id', 'title', 'description', 'file', 'created_at']


class MilestoneSerializer(serializers.ModelSerializer):
    """Serializer for Milestone model."""
    deliverables = DeliverableSerializer(many=True, read_only=True)
    
    class Meta:
        model = Milestone
        fields = [
            'id', 'title', 'description', 'amount', 'due_date', 'order',
            'status', 'started_at', 'submitted_at', 'approved_at', 'paid_at',
            'revision_notes', 'deliverables', 'created_at'
        ]


class MilestoneCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating milestones."""
    
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'amount', 'due_date']


class ContractListSerializer(serializers.ModelSerializer):
    """Serializer for Contract list view."""
    client = PublicUserSerializer(read_only=True)
    freelancer = PublicUserSerializer(read_only=True)
    progress = serializers.IntegerField(source='get_progress', read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id', 'title', 'client', 'freelancer', 'total_amount',
            'status', 'progress', 'start_date', 'end_date', 'created_at'
        ]


class ContractDetailSerializer(serializers.ModelSerializer):
    """Serializer for Contract detail view."""
    client = PublicUserSerializer(read_only=True)
    freelancer = PublicUserSerializer(read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    progress = serializers.IntegerField(source='get_progress', read_only=True)
    total_paid = serializers.DecimalField(source='get_total_paid', max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(source='get_remaining_amount', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id', 'title', 'description', 'client', 'freelancer', 'project',
            'total_amount', 'total_paid', 'remaining_amount', 'status', 'progress',
            'start_date', 'end_date', 'terms_accepted', 'milestones',
            'created_at', 'updated_at', 'completed_at'
        ]
