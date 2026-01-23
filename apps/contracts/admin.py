"""
Admin configuration for contracts app.
"""
from django.contrib import admin
from .models import Contract, Milestone, Deliverable, ContractActivity


class MilestoneInline(admin.TabularInline):
    """Inline for milestones."""
    model = Milestone
    extra = 0
    readonly_fields = ['started_at', 'submitted_at', 'approved_at', 'paid_at']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Admin configuration for Contract model."""
    list_display = [
        'title', 'client', 'freelancer', 'total_amount', 'status',
        'start_date', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'client__email', 'freelancer__email']
    raw_id_fields = ['project', 'proposal', 'client', 'freelancer']
    date_hierarchy = 'created_at'
    inlines = [MilestoneInline]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    """Admin configuration for Milestone model."""
    list_display = ['title', 'contract', 'amount', 'status', 'due_date']
    list_filter = ['status']
    search_fields = ['title', 'contract__title']
    raw_id_fields = ['contract']


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    """Admin configuration for Deliverable model."""
    list_display = ['title', 'milestone', 'created_at']
    raw_id_fields = ['milestone']


@admin.register(ContractActivity)
class ContractActivityAdmin(admin.ModelAdmin):
    """Admin configuration for ContractActivity model."""
    list_display = ['contract', 'user', 'activity_type', 'created_at']
    list_filter = ['activity_type']
    raw_id_fields = ['contract', 'user']
