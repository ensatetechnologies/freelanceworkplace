"""
Admin configuration for reviews app.
"""
from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""
    list_display = [
        'id', 'contract', 'reviewer', 'reviewee', 'type',
        'overall_rating', 'is_visible', 'created_at'
    ]
    list_filter = ['type', 'overall_rating', 'is_visible', 'created_at']
    search_fields = ['reviewer__email', 'reviewee__email', 'comment']
    raw_id_fields = ['contract', 'reviewer', 'reviewee']
    date_hierarchy = 'created_at'
