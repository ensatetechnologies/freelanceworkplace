"""
Signals for reviews app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review


@receiver(post_save, sender=Review)
def update_user_rating(sender, instance, created, **kwargs):
    """Update user's average rating when a review is created."""
    if created:
        reviewee = instance.reviewee
        
        # Calculate average rating
        avg_rating = Review.objects.filter(
            reviewee=reviewee,
            is_visible=True
        ).aggregate(avg=Avg('overall_rating'))['avg'] or 0
        
        total_reviews = Review.objects.filter(
            reviewee=reviewee,
            is_visible=True
        ).count()
        
        # Update profile
        if reviewee.role == 'freelancer':
            profile = reviewee.freelancer_profile
        else:
            profile = reviewee.client_profile
        
        if profile:
            profile.avg_rating = round(avg_rating, 2)
            profile.total_reviews = total_reviews
            profile.save(update_fields=['avg_rating', 'total_reviews'])


@receiver(post_save, sender=Review)
def check_both_reviewed(sender, instance, created, **kwargs):
    """Make reviews visible when both parties have reviewed."""
    if created:
        contract = instance.contract
        reviews = contract.reviews.all()
        
        if reviews.count() == 2:
            # Both parties have reviewed, make both visible
            reviews.update(is_visible=True)
