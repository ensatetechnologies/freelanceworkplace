"""
API views for reviews app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.accounts.models import User
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewCreateView(generics.CreateAPIView):
    """Create a review."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewCreateSerializer


class UserReviewsView(generics.ListAPIView):
    """List reviews for a user."""
    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        return Review.objects.filter(
            reviewee_id=user_pk,
            is_visible=True
        ).select_related('reviewer', 'contract')


class ContractReviewsView(generics.ListAPIView):
    """List reviews for a contract."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        contract_pk = self.kwargs.get('contract_pk')
        return Review.objects.filter(
            contract_id=contract_pk
        ).select_related('reviewer', 'reviewee')
