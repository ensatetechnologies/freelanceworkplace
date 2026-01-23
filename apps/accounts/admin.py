"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FreelancerProfile, ClientProfile, Skill


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ['email', 'username', 'role', 'is_verified', 'is_profile_complete', 'created_at']
    list_filter = ['role', 'is_verified', 'is_profile_complete', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'avatar', 'is_verified', 'is_profile_complete')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'role')
        }),
    )


@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    """Admin configuration for FreelancerProfile model."""
    list_display = ['user', 'title', 'hourly_rate', 'availability', 'avg_rating', 'completed_projects']
    list_filter = ['availability', 'experience_years']
    search_fields = ['user__email', 'user__username', 'title']
    raw_id_fields = ['user']


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """Admin configuration for ClientProfile model."""
    list_display = ['user', 'company_name', 'industry', 'total_spent', 'projects_posted']
    list_filter = ['company_size', 'industry']
    search_fields = ['user__email', 'user__username', 'company_name']
    raw_id_fields = ['user']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin configuration for Skill model."""
    list_display = ['name', 'category', 'slug']
    list_filter = ['category']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
