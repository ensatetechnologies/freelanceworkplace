"""
Admin configuration for payments app.
"""
from django.contrib import admin
from .models import EscrowAccount, Transaction, FreelancerWallet, WithdrawalRequest


@admin.register(EscrowAccount)
class EscrowAccountAdmin(admin.ModelAdmin):
    """Admin configuration for EscrowAccount model."""
    list_display = ['contract', 'total_funded', 'total_released', 'balance']
    raw_id_fields = ['contract']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model."""
    list_display = ['id', 'user', 'type', 'amount', 'fee', 'net_amount', 'status', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['user__email', 'payment_reference']
    raw_id_fields = ['user', 'contract', 'milestone']
    date_hierarchy = 'created_at'


@admin.register(FreelancerWallet)
class FreelancerWalletAdmin(admin.ModelAdmin):
    """Admin configuration for FreelancerWallet model."""
    list_display = ['user', 'balance', 'pending_balance', 'total_earned', 'total_withdrawn']
    search_fields = ['user__email']
    raw_id_fields = ['user']


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    """Admin configuration for WithdrawalRequest model."""
    list_display = ['id', 'wallet', 'amount', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    raw_id_fields = ['wallet']
    actions = ['approve_withdrawals', 'process_withdrawals']
    
    def approve_withdrawals(self, request, queryset):
        queryset.filter(status='pending').update(status='approved')
    approve_withdrawals.short_description = 'Approve selected withdrawals'
    
    def process_withdrawals(self, request, queryset):
        from .services import PaymentService
        service = PaymentService()
        for withdrawal in queryset.filter(status='approved'):
            try:
                service.process_withdrawal(withdrawal)
            except Exception:
                pass
    process_withdrawals.short_description = 'Process selected withdrawals'
