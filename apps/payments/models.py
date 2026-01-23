"""
Payment models for the application.
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal
from apps.core.models import BaseModel


class EscrowAccount(BaseModel):
    """Escrow account for contracts."""
    contract = models.OneToOneField(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='escrow'
    )
    total_funded = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_released = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'escrow_accounts'
    
    def __str__(self):
        return f'Escrow for {self.contract.title}'
    
    def fund(self, amount):
        """Add funds to escrow."""
        self.total_funded += Decimal(str(amount))
        self.balance += Decimal(str(amount))
        self.save()
    
    def release(self, amount):
        """Release funds from escrow."""
        amount = Decimal(str(amount))
        if amount > self.balance:
            raise ValueError('Insufficient escrow balance')
        self.total_released += amount
        self.balance -= amount
        self.save()


class Transaction(BaseModel):
    """Payment transactions."""
    
    class Type(models.TextChoices):
        ESCROW_FUND = 'escrow_fund', 'Escrow Funding'
        MILESTONE_RELEASE = 'milestone_release', 'Milestone Release'
        WITHDRAWAL = 'withdrawal', 'Withdrawal'
        REFUND = 'refund', 'Refund'
        PLATFORM_FEE = 'platform_fee', 'Platform Fee'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions'
    )
    milestone = models.ForeignKey(
        'contracts.Milestone',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Simulated payment reference
    payment_reference = models.CharField(max_length=100, blank=True)
    
    description = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.type} - ${self.amount} - {self.status}'


class FreelancerWallet(BaseModel):
    """Freelancer earnings wallet."""
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'freelancer_wallets'
    
    def __str__(self):
        return f'Wallet: {self.user.email}'
    
    def add_earnings(self, amount):
        """Add earnings to wallet."""
        amount = Decimal(str(amount))
        self.balance += amount
        self.total_earned += amount
        self.save()
    
    def withdraw(self, amount):
        """Withdraw from wallet."""
        amount = Decimal(str(amount))
        if amount > self.balance:
            raise ValueError('Insufficient balance')
        self.balance -= amount
        self.total_withdrawn += amount
        self.save()


class WithdrawalRequest(BaseModel):
    """Freelancer withdrawal requests."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'
    
    wallet = models.ForeignKey(
        FreelancerWallet,
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Simulated bank info
    bank_name = models.CharField(max_length=100, blank=True)
    account_last_four = models.CharField(max_length=4, blank=True)
    
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'withdrawal_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Withdrawal ${self.amount} - {self.status}'
    
    def approve(self):
        """Approve withdrawal request."""
        self.status = self.Status.APPROVED
        self.save()
    
    def process(self):
        """Process withdrawal."""
        self.status = self.Status.PROCESSING
        self.save()
    
    def complete(self):
        """Complete withdrawal."""
        self.status = self.Status.COMPLETED
        self.processed_at = timezone.now()
        self.wallet.withdraw(self.amount)
        self.save()
    
    def reject(self, notes=''):
        """Reject withdrawal request."""
        self.status = self.Status.REJECTED
        self.admin_notes = notes
        self.save()
