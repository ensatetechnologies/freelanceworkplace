"""
Serializers for reviews app.
"""
from rest_framework import serializers
from apps.accounts.serializers import PublicUserSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    reviewer = PublicUserSerializer(read_only=True)
    reviewee = PublicUserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'contract', 'reviewer', 'reviewee', 'type',
            'overall_rating', 'quality_rating', 'communication_rating',
            'timeliness_rating', 'professionalism_rating', 'clarity_rating',
            'payment_rating', 'comment', 'is_visible', 'created_at'
        ]
        read_only_fields = ['reviewer', 'reviewee', 'type', 'is_visible']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = Review
        fields = [
            'contract', 'overall_rating', 'quality_rating', 'communication_rating',
            'timeliness_rating', 'professionalism_rating', 'clarity_rating',
            'payment_rating', 'comment'
        ]
    
    def validate_contract(self, value):
        user = self.context['request'].user
        
        if value.status != 'completed':
            raise serializers.ValidationError('Contract must be completed to leave a review.')
        
        if user not in [value.client, value.freelancer]:
            raise serializers.ValidationError('You are not part of this contract.')
        
        if Review.objects.filter(contract=value, reviewer=user).exists():
            raise serializers.ValidationError('You have already reviewed this contract.')
        
        return value
    
    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
