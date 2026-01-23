"""
Project models for the application.
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.utils import project_attachment_path, generate_unique_slug


class Category(BaseModel):
    """Project categories."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)
        super().save(*args, **kwargs)
    
    def get_project_count(self):
        return self.projects.filter(status='open').count()


class Project(BaseModel):
    """Project listings."""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        UNDER_REVIEW = 'under_review', 'Under Review'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        DISPUTED = 'disputed', 'Disputed'
    
    class BudgetType(models.TextChoices):
        FIXED = 'fixed', 'Fixed Price'
        HOURLY = 'hourly', 'Hourly Rate'
        MILESTONE = 'milestone', 'Milestone Based'
    
    class ExperienceLevel(models.TextChoices):
        ENTRY = 'entry', 'Entry Level'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        EXPERT = 'expert', 'Expert'
    
    class Duration(models.TextChoices):
        LESS_THAN_WEEK = 'less_than_week', 'Less than a week'
        ONE_TO_TWO_WEEKS = '1_2_weeks', '1-2 weeks'
        TWO_TO_FOUR_WEEKS = '2_4_weeks', '2-4 weeks'
        ONE_TO_THREE_MONTHS = '1_3_months', '1-3 months'
        THREE_TO_SIX_MONTHS = '3_6_months', '3-6 months'
        MORE_THAN_SIX_MONTHS = 'more_than_6_months', 'More than 6 months'
    
    client = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='projects'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField()
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='projects'
    )
    skills_required = models.JSONField(default=list)
    
    budget_type = models.CharField(max_length=20, choices=BudgetType.choices)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)
    
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices)
    estimated_duration = models.CharField(max_length=30, choices=Duration.choices)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    deadline = models.DateField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    views_count = models.PositiveIntegerField(default=0)
    proposals_count = models.PositiveIntegerField(default=0)
    
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['client']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Project, self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.slug})
    
    def publish(self):
        """Publish the project."""
        self.status = self.Status.OPEN
        self.published_at = timezone.now()
        self.save()
    
    def get_skills_list(self):
        """Return skills as a list."""
        if isinstance(self.skills_required, list):
            return self.skills_required
        return []
    
    def get_budget_display(self):
        """Return formatted budget display."""
        if self.budget_type == self.BudgetType.HOURLY:
            return f'${self.budget_min} - ${self.budget_max}/hr'
        return f'${self.budget_min} - ${self.budget_max}'
    
    def increment_views(self):
        """Increment view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ProjectAttachment(BaseModel):
    """File attachments for projects."""
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(upload_to=project_attachment_path)
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'project_attachments'
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        if self.file:
            self.filename = self.file.name
            self.file_size = self.file.size
            import os
            self.file_type = os.path.splitext(self.file.name)[1].lower()
        super().save(*args, **kwargs)


class SavedProject(BaseModel):
    """Saved/bookmarked projects by freelancers."""
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='saved_projects'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    
    class Meta:
        db_table = 'saved_projects'
        unique_together = ['user', 'project']
    
    def __str__(self):
        return f'{self.user.email} saved {self.project.title}'
