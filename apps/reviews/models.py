"""
Review models for the application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel


class Review(BaseModel):
    """Reviews after project completion."""
    
    class Type(models.TextChoices):
        CLIENT_TO_FREELANCER = 'client_to_freelancer', 'Client to Freelancer'
        FREELANCER_TO_CLIENT = 'freelancer_to_client', 'Freelancer to Client'
    
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    reviewee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    
    type = models.CharField(max_length=25, choices=Type.choices)
    
    overall_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Category ratings (for client reviewing freelancer)
    quality_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communication_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    timeliness_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    professionalism_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Category ratings (for freelancer reviewing client)
    clarity_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    payment_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    comment = models.TextField()
    
    is_visible = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'reviews'
        unique_together = ['contract', 'reviewer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.reviewer.get_full_name()} → {self.reviewee.get_full_name()} ({self.overall_rating}★)'
    
    def save(self, *args, **kwargs):
        # Auto-set review type
        if self.contract.client == self.reviewer:
            self.type = self.Type.CLIENT_TO_FREELANCER
            self.reviewee = self.contract.freelancer
        else:
            self.type = self.Type.FREELANCER_TO_CLIENT
            self.reviewee = self.contract.client
        
        super().save(*args, **kwargs)
    
    def make_visible(self):
        """Make the review visible after both parties have reviewed."""
        self.is_visible = True
        self.save(update_fields=['is_visible'])
