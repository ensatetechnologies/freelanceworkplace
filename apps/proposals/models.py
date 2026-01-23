"""
Proposal models for the application.
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.utils import proposal_attachment_path


class Proposal(BaseModel):
    """Freelancer proposals/bids on projects."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='proposals'
    )
    freelancer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='proposals'
    )
    
    cover_letter = models.TextField(help_text='Explain why you are the best fit for this project')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.CharField(max_length=100)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'proposals'
        unique_together = ['project', 'freelancer']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['freelancer', 'status']),
        ]
    
    def __str__(self):
        return f'{self.freelancer.get_full_name()} - {self.project.title}'
    
    def get_absolute_url(self):
        return reverse('proposals:detail', kwargs={'pk': self.pk})
    
    def mark_viewed(self):
        """Mark proposal as viewed."""
        if not self.is_viewed:
            self.is_viewed = True
            self.viewed_at = timezone.now()
            self.save(update_fields=['is_viewed', 'viewed_at'])
    
    def accept(self):
        """Accept the proposal."""
        self.status = self.Status.ACCEPTED
        self.save(update_fields=['status'])
        
        # Update project proposals count
        self.project.proposals.exclude(pk=self.pk).update(status=self.Status.REJECTED)
        self.project.status = 'in_progress'
        self.project.save(update_fields=['status'])
    
    def reject(self):
        """Reject the proposal."""
        self.status = self.Status.REJECTED
        self.save(update_fields=['status'])
    
    def shortlist(self):
        """Shortlist the proposal."""
        self.status = self.Status.SHORTLISTED
        self.save(update_fields=['status'])
    
    def withdraw(self):
        """Withdraw the proposal."""
        self.status = self.Status.WITHDRAWN
        self.save(update_fields=['status'])
        
        # Decrement project proposals count
        self.project.proposals_count -= 1
        self.project.save(update_fields=['proposals_count'])


class ProposalAttachment(BaseModel):
    """Sample work attachments for proposals."""
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to=proposal_attachment_path)
    filename = models.CharField(max_length=255)
    description = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'proposal_attachments'
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        if self.file and not self.filename:
            self.filename = self.file.name
        super().save(*args, **kwargs)
