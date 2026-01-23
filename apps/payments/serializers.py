"""
Serializers for payments app.
"""
from rest_framework import serializers
from .models import Transaction, EscrowAccount, FreelancerWallet, WithdrawalRequest


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'amount', 'fee', 'net_amount', 'status',
            'payment_reference', 'description', 'created_at'
        ]


class EscrowSerializer(serializers.ModelSerializer):
    """Serializer for EscrowAccount model."""
    
    class Meta:
        model = EscrowAccount
        fields = ['id', 'total_funded', 'total_released', 'balance', 'created_at']


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for FreelancerWallet model."""
    
    class Meta:
        model = FreelancerWallet
        fields = [
            'id', 'balance', 'pending_balance', 'total_earned',
            'total_withdrawn', 'created_at'
        ]


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    """Serializer for WithdrawalRequest model."""
    
    class Meta:
        model = WithdrawalRequest
        fields = [
            'id', 'amount', 'status', 'bank_name', 'account_last_four',
            'processed_at', 'created_at'
        ]


class FundEscrowSerializer(serializers.Serializer):
    """Serializer for funding escrow."""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


class WithdrawalSerializer(serializers.Serializer):
    """Serializer for withdrawal requests."""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    bank_name = serializers.CharField(max_length=100, default='Simulated Bank')
    account_last_four = serializers.CharField(max_length=4, default='1234')
