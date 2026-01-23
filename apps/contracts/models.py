"""
Contract models for the application.
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.utils import deliverable_upload_path


class Contract(BaseModel):
    """Contracts created from accepted proposals."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        DISPUTED = 'disputed', 'Disputed'
    
    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='contract'
    )
    proposal = models.OneToOneField(
        'proposals.Proposal',
        on_delete=models.CASCADE,
        related_name='contract'
    )
    client = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='client_contracts'
    )
    freelancer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='freelancer_contracts'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'contracts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['freelancer']),
        ]
    
    def __str__(self):
        return f'{self.title} - {self.client.get_full_name()} & {self.freelancer.get_full_name()}'
    
    def get_absolute_url(self):
        return reverse('contracts:detail', kwargs={'pk': self.pk})
    
    def get_progress(self):
        """Calculate milestone completion progress."""
        total = self.milestones.count()
        if total == 0:
            return 0
        completed = self.milestones.filter(status__in=['approved', 'paid']).count()
        return int((completed / total) * 100)
    
    def get_total_paid(self):
        """Get total amount paid."""
        return self.milestones.filter(status='paid').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    def get_remaining_amount(self):
        """Get remaining amount to be paid."""
        return self.total_amount - self.get_total_paid()
    
    def complete(self):
        """Mark contract as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.end_date = timezone.now().date()
        self.save()
        
        # Update project status
        self.project.status = 'completed'
        self.project.save(update_fields=['status'])
        
        # Update freelancer stats
        profile = self.freelancer.freelancer_profile
        profile.completed_projects += 1
        profile.total_earnings += self.total_amount
        profile.save()
    
    def accept_terms(self):
        """Accept contract terms."""
        self.terms_accepted = True
        self.terms_accepted_at = timezone.now()
        self.save(update_fields=['terms_accepted', 'terms_accepted_at'])


class Milestone(BaseModel):
    """Contract milestones."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        SUBMITTED = 'submitted', 'Submitted for Review'
        REVISION_REQUESTED = 'revision', 'Revision Requested'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
    
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    order = models.PositiveIntegerField(default=0)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    revision_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'milestones'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f'{self.contract.title} - {self.title}'
    
    def start(self):
        """Start working on milestone."""
        self.status = self.Status.IN_PROGRESS
        self.started_at = timezone.now()
        self.save()
    
    def submit(self):
        """Submit milestone for review."""
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()
        self.save()
    
    def approve(self):
        """Approve milestone."""
        self.status = self.Status.APPROVED
        self.approved_at = timezone.now()
        self.save()
    
    def request_revision(self, notes):
        """Request revision with notes."""
        self.status = self.Status.REVISION_REQUESTED
        self.revision_notes = notes
        self.save()
    
    def mark_paid(self):
        """Mark milestone as paid."""
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save()


class Deliverable(BaseModel):
    """Work deliverables for milestones."""
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
        related_name='deliverables'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=deliverable_upload_path)
    
    class Meta:
        db_table = 'deliverables'
    
    def __str__(self):
        return self.title


class ContractActivity(BaseModel):
    """Activity log for contracts."""
    
    class ActivityType(models.TextChoices):
        CONTRACT_CREATED = 'contract_created', 'Contract Created'
        MILESTONE_ADDED = 'milestone_added', 'Milestone Added'
        MILESTONE_STARTED = 'milestone_started', 'Milestone Started'
        MILESTONE_SUBMITTED = 'milestone_submitted', 'Milestone Submitted'
        MILESTONE_APPROVED = 'milestone_approved', 'Milestone Approved'
        MILESTONE_REVISION = 'milestone_revision', 'Revision Requested'
        PAYMENT_MADE = 'payment_made', 'Payment Made'
        CONTRACT_COMPLETED = 'contract_completed', 'Contract Completed'
        DISPUTE_OPENED = 'dispute_opened', 'Dispute Opened'
    
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE
    )
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices)
    description = models.TextField()
    
    class Meta:
        db_table = 'contract_activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.contract.title} - {self.activity_type}'
