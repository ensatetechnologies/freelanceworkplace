"""
API views for messaging app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.models import User
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    SendMessageSerializer
)


class ConversationListView(generics.ListAPIView):
    """List user's conversations."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants').order_by('-last_message_at')


class ConversationDetailView(generics.RetrieveAPIView):
    """Get conversation details with messages."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationDetailSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('messages', 'participants')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.mark_as_read(request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class StartConversationView(APIView):
    """Start a new conversation."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        recipient_id = request.data.get('recipient_id')
        initial_message = request.data.get('message', '')
        
        try:
            recipient = User.objects.get(pk=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if conversation exists
        existing = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=recipient).first()
        
        if existing:
            if initial_message:
                Message.objects.create(
                    conversation=existing,
                    sender=request.user,
                    content=initial_message
                )
            return Response(ConversationDetailSerializer(existing, context={'request': request}).data)
        
        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
        
        if initial_message:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=initial_message
            )
        
        return Response(
            ConversationDetailSerializer(conversation, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class SendMessageView(APIView):
    """Send a message in a conversation."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, conversation_pk):
        conversation = Conversation.objects.filter(
            pk=conversation_pk,
            participants=request.user
        ).first()
        
        if not conversation:
            return Response(
                {'error': 'Conversation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SendMessageSerializer(
            data=request.data,
            context={'request': request, 'conversation': conversation}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FetchMessagesView(generics.ListAPIView):
    """Fetch messages from a conversation."""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        conversation_pk = self.kwargs.get('conversation_pk')
        conversation = Conversation.objects.filter(
            pk=conversation_pk,
            participants=self.request.user
        ).first()
        
        if not conversation:
            return Message.objects.none()
        
        # Mark as read
        conversation.mark_as_read(self.request.user)
        
        last_id = self.request.query_params.get('last_id')
        queryset = conversation.messages.select_related('sender')
        
        if last_id:
            queryset = queryset.filter(id__gt=last_id)
        
        return queryset[:50]


class MarkReadView(APIView):
    """Mark a message as read."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        message = Message.objects.filter(
            pk=pk,
            conversation__participants=request.user
        ).first()
        
        if not message:
            return Response(
                {'error': 'Message not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not message.is_read and message.sender != request.user:
            from django.utils import timezone
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        
        return Response({'message': 'Marked as read.'})
