"""
API views for payments app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsFreelancer, IsClient
from apps.contracts.models import Contract, Milestone
from .models import Transaction, FreelancerWallet, WithdrawalRequest
from .serializers import (
    TransactionSerializer,
    WalletSerializer,
    WithdrawalRequestSerializer,
    FundEscrowSerializer,
    WithdrawalSerializer
)
from .services import PaymentService


class TransactionListView(generics.ListAPIView):
    """List user's transactions."""
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class WalletView(generics.RetrieveAPIView):
    """Get freelancer wallet."""
    permission_classes = [IsAuthenticated, IsFreelancer]
    serializer_class = WalletSerializer
    
    def get_object(self):
        wallet, _ = FreelancerWallet.objects.get_or_create(user=self.request.user)
        return wallet


class FundEscrowView(APIView):
    """Fund escrow for a contract."""
    permission_classes = [IsAuthenticated, IsClient]
    
    def post(self, request, contract_pk):
        contract = Contract.objects.filter(
            pk=contract_pk, client=request.user, status='active'
        ).first()
        
        if not contract:
            return Response(
                {'error': 'Contract not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FundEscrowSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = PaymentService()
        try:
            result = service.fund_escrow(
                contract,
                serializer.validated_data['amount'],
                request.user
            )
            return Response({
                'success': True,
                'message': 'Escrow funded successfully.',
                'reference': result['reference'],
                'escrow_balance': str(result['escrow_balance'])
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReleaseMilestonePaymentView(APIView):
    """Release milestone payment."""
    permission_classes = [IsAuthenticated, IsClient]
    
    def post(self, request, milestone_pk):
        milestone = Milestone.objects.filter(
            pk=milestone_pk,
            contract__client=request.user,
            status='approved'
        ).first()
        
        if not milestone:
            return Response(
                {'error': 'Milestone not found or not approved.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service = PaymentService()
        try:
            result = service.release_milestone_payment(milestone, request.user)
            return Response({
                'success': True,
                'message': 'Payment released successfully.',
                'reference': result['reference'],
                'net_amount': str(result['net_amount']),
                'fee': str(result['fee'])
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WithdrawalListCreateView(generics.ListCreateAPIView):
    """List and create withdrawal requests."""
    permission_classes = [IsAuthenticated, IsFreelancer]
    serializer_class = WithdrawalRequestSerializer
    
    def get_queryset(self):
        wallet, _ = FreelancerWallet.objects.get_or_create(user=self.request.user)
        return WithdrawalRequest.objects.filter(wallet=wallet)
    
    def create(self, request, *args, **kwargs):
        wallet, _ = FreelancerWallet.objects.get_or_create(user=request.user)
        
        serializer = WithdrawalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        amount = serializer.validated_data['amount']
        
        if amount > wallet.balance:
            return Response(
                {'error': 'Insufficient balance.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        withdrawal = WithdrawalRequest.objects.create(
            wallet=wallet,
            amount=amount,
            bank_name=serializer.validated_data.get('bank_name', 'Simulated Bank'),
            account_last_four=serializer.validated_data.get('account_last_four', '1234')
        )
        
        return Response(
            WithdrawalRequestSerializer(withdrawal).data,
            status=status.HTTP_201_CREATED
        )
