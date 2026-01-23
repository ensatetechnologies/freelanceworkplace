"""
Admin configuration for proposals app.
"""
from django.contrib import admin
from .models import Proposal, ProposalAttachment


class ProposalAttachmentInline(admin.TabularInline):
    """Inline for proposal attachments."""
    model = ProposalAttachment
    extra = 0


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    """Admin configuration for Proposal model."""
    list_display = [
        'id', 'project', 'freelancer', 'bid_amount', 'status',
        'is_viewed', 'created_at'
    ]
    list_filter = ['status', 'is_viewed', 'created_at']
    search_fields = ['project__title', 'freelancer__email', 'cover_letter']
    raw_id_fields = ['project', 'freelancer']
    date_hierarchy = 'created_at'
    inlines = [ProposalAttachmentInline]
    
    readonly_fields = ['viewed_at']
