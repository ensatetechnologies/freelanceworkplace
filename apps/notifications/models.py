"""
Notification models for the application.
"""
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel


class Notification(BaseModel):
    """User notifications."""
    
    class Type(models.TextChoices):
        NEW_PROPOSAL = 'new_proposal', 'New Proposal'
        PROPOSAL_ACCEPTED = 'proposal_accepted', 'Proposal Accepted'
        PROPOSAL_REJECTED = 'proposal_rejected', 'Proposal Rejected'
        NEW_MESSAGE = 'new_message', 'New Message'
        MILESTONE_APPROVED = 'milestone_approved', 'Milestone Approved'
        MILESTONE_REVISION = 'milestone_revision', 'Revision Requested'
        PAYMENT_RECEIVED = 'payment_received', 'Payment Received'
        REVIEW_RECEIVED = 'review_received', 'Review Received'
        CONTRACT_STARTED = 'contract_started', 'Contract Started'
        CONTRACT_COMPLETED = 'contract_completed', 'Contract Completed'
        DISPUTE_OPENED = 'dispute_opened', 'Dispute Opened'
        DISPUTE_RESOLVED = 'dispute_resolved', 'Dispute Resolved'
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    action_url = models.CharField(max_length=255, blank=True)
    
    # Generic relation fields for linking to related objects
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.email}: {self.title}'
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


def create_notification(user, notification_type, title, message, action_url='', related_object=None):
    """Helper function to create notifications."""
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
        related_object_type=related_object.__class__.__name__ if related_object else '',
        related_object_id=related_object.pk if related_object else None
    )
    return notification
