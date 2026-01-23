"""
API views for notifications app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """List user's notifications."""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class MarkAsReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        notification = Notification.objects.filter(
            pk=pk, user=request.user
        ).first()
        
        if not notification:
            return Response(
                {'error': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notification.mark_as_read()
        return Response({'success': True})


class MarkAllAsReadView(APIView):
    """Mark all notifications as read."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'success': True})


class UnreadCountView(APIView):
    """Get unread notification count."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response({'unread_count': count})
