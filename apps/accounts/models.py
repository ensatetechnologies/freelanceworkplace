"""
User and profile models for the application.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from apps.core.models import BaseModel, TimeStampedModel
from apps.core.utils import avatar_upload_path


class User(AbstractUser, TimeStampedModel):
    """Custom user model."""
    
    class Role(models.TextChoices):
        FREELANCER = 'freelancer', 'Freelancer'
        CLIENT = 'client', 'Client'
        ADMIN = 'admin', 'Admin'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username
    
    def get_profile(self):
        """Get the user's role-specific profile."""
        if self.role == self.Role.FREELANCER:
            return getattr(self, 'freelancer_profile', None)
        elif self.role == self.Role.CLIENT:
            return getattr(self, 'client_profile', None)
        return None
    
    def get_avatar_url(self):
        """Get avatar URL or default."""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class FreelancerProfile(BaseModel):
    """Extended profile for freelancers."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='freelancer_profile'
    )
    title = models.CharField(max_length=100, blank=True, default='', help_text='Professional title, e.g. "Full Stack Developer"')
    bio = models.TextField(max_length=2000, blank=True, default='', help_text='Tell clients about yourself')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    skills = models.JSONField(default=list, help_text='List of skills')
    experience_years = models.PositiveIntegerField(default=0)
    portfolio_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    class Availability(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        PARTIALLY_AVAILABLE = 'partial', 'Partially Available'
        NOT_AVAILABLE = 'unavailable', 'Not Available'
    
    availability = models.CharField(
        max_length=20, 
        choices=Availability.choices, 
        default=Availability.AVAILABLE
    )
    
    # Stats (updated by signals)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    completed_projects = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'freelancer_profiles'
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.title}'
    
    def get_skills_list(self):
        """Return skills as a list."""
        if isinstance(self.skills, list):
            return self.skills
        return []


class ClientProfile(BaseModel):
    """Extended profile for clients."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_profile'
    )
    company_name = models.CharField(max_length=200, blank=True)
    company_website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    class CompanySize(models.TextChoices):
        SOLO = '1', 'Just me'
        SMALL = '2-10', '2-10 employees'
        MEDIUM = '11-50', '11-50 employees'
        LARGE = '51-200', '51-200 employees'
        ENTERPRISE = '200+', '200+ employees'
    
    company_size = models.CharField(
        max_length=20, 
        choices=CompanySize.choices, 
        blank=True
    )
    
    # Stats (updated by signals)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    projects_posted = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'client_profiles'
    
    def __str__(self):
        if self.company_name:
            return f'{self.user.get_full_name()} - {self.company_name}'
        return self.user.get_full_name()


class Skill(BaseModel):
    """Skill tags for categorization."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    class Category(models.TextChoices):
        PROGRAMMING = 'programming', 'Programming'
        DESIGN = 'design', 'Design'
        WRITING = 'writing', 'Writing'
        MARKETING = 'marketing', 'Marketing'
        BUSINESS = 'business', 'Business'
        OTHER = 'other', 'Other'
    
    category = models.CharField(
        max_length=20, 
        choices=Category.choices, 
        default=Category.OTHER
    )
    
    class Meta:
        db_table = 'skills'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
