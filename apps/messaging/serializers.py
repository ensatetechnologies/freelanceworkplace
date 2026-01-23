"""
Serializers for messaging app.
"""
from rest_framework import serializers
from apps.accounts.serializers import PublicUserSerializer
from .models import Conversation, Message, MessageAttachment


class MessageAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for MessageAttachment model."""
    
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file', 'filename', 'file_type', 'file_size']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender = PublicUserSerializer(read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'content', 'is_read', 'read_at',
            'attachments', 'created_at'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    participants = PublicUserSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'last_message_at', 'last_message_preview',
            'unread_count', 'created_at'
        ]
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_unread_count(request.user)
        return 0


class ConversationDetailSerializer(ConversationSerializer):
    """Serializer for Conversation detail with messages."""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending messages."""
    content = serializers.CharField()
    
    def create(self, validated_data):
        return Message.objects.create(
            conversation=self.context['conversation'],
            sender=self.context['request'].user,
            content=validated_data['content']
        )
