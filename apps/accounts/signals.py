"""
Signals for accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, FreelancerProfile, ClientProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created."""
    if created:
        if instance.role == User.Role.FREELANCER:
            FreelancerProfile.objects.get_or_create(user=instance)
        elif instance.role == User.Role.CLIENT:
            ClientProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when user is saved."""
    if instance.role == User.Role.FREELANCER:
        if hasattr(instance, 'freelancer_profile'):
            instance.freelancer_profile.save()
    elif instance.role == User.Role.CLIENT:
        if hasattr(instance, 'client_profile'):
            instance.client_profile.save()
