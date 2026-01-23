"""
Admin configuration for projects app.
"""
from django.contrib import admin
from .models import Category, Project, ProjectAttachment, SavedProject


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ['name', 'slug', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


class ProjectAttachmentInline(admin.TabularInline):
    """Inline for project attachments."""
    model = ProjectAttachment
    extra = 0
    readonly_fields = ['filename', 'file_size', 'file_type']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""
    list_display = [
        'title', 'client', 'category', 'status', 'budget_type',
        'budget_min', 'budget_max', 'proposals_count', 'created_at'
    ]
    list_filter = ['status', 'budget_type', 'experience_level', 'category', 'is_featured']
    search_fields = ['title', 'description', 'client__email']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['client', 'category']
    date_hierarchy = 'created_at'
    inlines = [ProjectAttachmentInline]
    
    fieldsets = (
        (None, {
            'fields': ('client', 'title', 'slug', 'description', 'category')
        }),
        ('Requirements', {
            'fields': ('skills_required', 'experience_level', 'estimated_duration')
        }),
        ('Budget', {
            'fields': ('budget_type', 'budget_min', 'budget_max')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_urgent', 'deadline', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views_count', 'proposals_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedProject)
class SavedProjectAdmin(admin.ModelAdmin):
    """Admin configuration for SavedProject model."""
    list_display = ['user', 'project', 'created_at']
    raw_id_fields = ['user', 'project']
