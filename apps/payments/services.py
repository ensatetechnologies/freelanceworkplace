"""
Simulated payment gateway services.

This module provides a simulated payment gateway for local development.
All payments are simulated and no real money is transferred.
"""
import uuid
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

from .models import Transaction, EscrowAccount, FreelancerWallet


PLATFORM_FEE_PERCENT = Decimal(str(settings.PLATFORM_FEE_PERCENT))


class SimulatedPaymentGateway:
    """
    Simulated payment gateway for local development.
    
    This class simulates payment operations without connecting
    to a real payment provider.
    """
    
    @staticmethod
    def generate_reference():
        """Generate a simulated payment reference."""
        return f'SIM_{uuid.uuid4().hex[:16].upper()}'
    
    @staticmethod
    def calculate_platform_fee(amount):
        """Calculate platform fee."""
        amount = Decimal(str(amount))
        return (amount * PLATFORM_FEE_PERCENT / 100).quantize(Decimal('0.01'))
    
    @staticmethod
    def calculate_net_amount(amount):
        """Calculate net amount after platform fee."""
        amount = Decimal(str(amount))
        fee = SimulatedPaymentGateway.calculate_platform_fee(amount)
        return amount - fee
    
    @classmethod
    def process_payment(cls, amount, description=''):
        """
        Simulate processing a payment.
        
        In a real implementation, this would connect to Stripe/PayPal.
        Returns a simulated successful payment response.
        """
        return {
            'success': True,
            'reference': cls.generate_reference(),
            'amount': Decimal(str(amount)),
            'status': 'completed',
            'message': 'Payment processed successfully (simulated)',
            'processed_at': timezone.now().isoformat()
        }
    
    @classmethod
    def process_transfer(cls, amount, destination=''):
        """
        Simulate processing a transfer to a freelancer.
        
        In a real implementation, this would transfer funds to
        the freelancer's connected account.
        """
        return {
            'success': True,
            'reference': cls.generate_reference(),
            'amount': Decimal(str(amount)),
            'status': 'completed',
            'message': 'Transfer completed successfully (simulated)',
            'processed_at': timezone.now().isoformat()
        }
    
    @classmethod
    def process_refund(cls, amount, original_reference=''):
        """Simulate processing a refund."""
        return {
            'success': True,
            'reference': cls.generate_reference(),
            'amount': Decimal(str(amount)),
            'status': 'completed',
            'message': 'Refund processed successfully (simulated)',
            'processed_at': timezone.now().isoformat()
        }


class PaymentService:
    """Service class for handling payments."""
    
    def __init__(self):
        self.gateway = SimulatedPaymentGateway()
    
    def fund_escrow(self, contract, amount, user):
        """
        Fund escrow account for a contract.
        
        Creates or updates the escrow account and records the transaction.
        """
        amount = Decimal(str(amount))
        
        # Process payment through simulated gateway
        result = self.gateway.process_payment(
            amount,
            f'Escrow funding for: {contract.title}'
        )
        
        if not result['success']:
            raise Exception(result.get('message', 'Payment failed'))
        
        # Get or create escrow account
        escrow, created = EscrowAccount.objects.get_or_create(contract=contract)
        escrow.fund(amount)
        
        # Record transaction
        transaction = Transaction.objects.create(
            user=user,
            contract=contract,
            type=Transaction.Type.ESCROW_FUND,
            amount=amount,
            fee=0,
            net_amount=amount,
            status=Transaction.Status.COMPLETED,
            payment_reference=result['reference'],
            description=f'Escrow funding for: {contract.title}'
        )
        
        return {
            'success': True,
            'transaction': transaction,
            'escrow_balance': escrow.balance,
            'reference': result['reference']
        }
    
    def release_milestone_payment(self, milestone, user):
        """
        Release payment for a milestone.
        
        Transfers funds from escrow to freelancer's wallet,
        deducting platform fee.
        """
        contract = milestone.contract
        amount = milestone.amount
        
        # Get escrow account
        try:
            escrow = contract.escrow
        except EscrowAccount.DoesNotExist:
            raise Exception('Escrow account not found')
        
        if escrow.balance < amount:
            raise Exception('Insufficient escrow balance')
        
        # Calculate fee and net amount
        fee = self.gateway.calculate_platform_fee(amount)
        net_amount = self.gateway.calculate_net_amount(amount)
        
        # Process transfer
        result = self.gateway.process_transfer(
            net_amount,
            f'Payment for milestone: {milestone.title}'
        )
        
        if not result['success']:
            raise Exception(result.get('message', 'Transfer failed'))
        
        # Release from escrow
        escrow.release(amount)
        
        # Get or create freelancer wallet
        wallet, _ = FreelancerWallet.objects.get_or_create(
            user=contract.freelancer
        )
        wallet.add_earnings(net_amount)
        
        # Mark milestone as paid
        milestone.mark_paid()
        
        # Record transaction for freelancer
        transaction = Transaction.objects.create(
            user=contract.freelancer,
            contract=contract,
            milestone=milestone,
            type=Transaction.Type.MILESTONE_RELEASE,
            amount=amount,
            fee=fee,
            net_amount=net_amount,
            status=Transaction.Status.COMPLETED,
            payment_reference=result['reference'],
            description=f'Payment for milestone: {milestone.title}'
        )
        
        # Record platform fee transaction
        Transaction.objects.create(
            user=contract.client,
            contract=contract,
            milestone=milestone,
            type=Transaction.Type.PLATFORM_FEE,
            amount=fee,
            fee=0,
            net_amount=fee,
            status=Transaction.Status.COMPLETED,
            description=f'Platform fee for: {milestone.title}'
        )
        
        return {
            'success': True,
            'transaction': transaction,
            'net_amount': net_amount,
            'fee': fee,
            'wallet_balance': wallet.balance,
            'reference': result['reference']
        }
    
    def process_withdrawal(self, withdrawal_request):
        """
        Process a withdrawal request.
        
        Transfers funds from freelancer wallet to their bank account.
        """
        amount = withdrawal_request.amount
        wallet = withdrawal_request.wallet
        
        if wallet.balance < amount:
            raise Exception('Insufficient wallet balance')
        
        # Process transfer
        result = self.gateway.process_transfer(
            amount,
            f'Withdrawal to bank account'
        )
        
        if not result['success']:
            raise Exception(result.get('message', 'Withdrawal failed'))
        
        # Complete withdrawal
        withdrawal_request.complete()
        
        # Record transaction
        transaction = Transaction.objects.create(
            user=wallet.user,
            type=Transaction.Type.WITHDRAWAL,
            amount=amount,
            fee=0,
            net_amount=amount,
            status=Transaction.Status.COMPLETED,
            payment_reference=result['reference'],
            description='Withdrawal to bank account'
        )
        
        return {
            'success': True,
            'transaction': transaction,
            'wallet_balance': wallet.balance,
            'reference': result['reference']
        }
