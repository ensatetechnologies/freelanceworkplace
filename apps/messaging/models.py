"""
Messaging models for the application.
"""
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.utils import message_attachment_path


class Conversation(BaseModel):
    """Chat conversations between users."""
    participants = models.ManyToManyField(
        'accounts.User',
        related_name='conversations'
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )
    
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_preview = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-last_message_at']
    
    def __str__(self):
        participants = self.participants.all()[:2]
        names = [p.get_full_name() for p in participants]
        return ' & '.join(names)
    
    def get_other_participant(self, user):
        """Get the other participant in a conversation."""
        return self.participants.exclude(pk=user.pk).first()
    
    def get_unread_count(self, user):
        """Get unread message count for a user."""
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def mark_as_read(self, user):
        """Mark all messages as read for a user."""
        self.messages.filter(is_read=False).exclude(sender=user).update(
            is_read=True,
            read_at=timezone.now()
        )


class Message(BaseModel):
    """Individual chat messages."""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    content = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.sender.get_full_name()}: {self.content[:50]}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update conversation last message
        self.conversation.last_message_at = self.created_at
        self.conversation.last_message_preview = self.content[:100]
        self.conversation.save(update_fields=['last_message_at', 'last_message_preview'])


class MessageAttachment(BaseModel):
    """File attachments for messages."""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to=message_attachment_path)
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'message_attachments'
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        if self.file:
            import os
            self.filename = os.path.basename(self.file.name)
            self.file_type = os.path.splitext(self.file.name)[1].lower()
            self.file_size = self.file.size
        super().save(*args, **kwargs)
