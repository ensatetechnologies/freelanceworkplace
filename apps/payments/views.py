"""
Views for payments app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse

from apps.core.mixins import FreelancerRequiredMixin, ClientRequiredMixin
from apps.contracts.models import Contract, Milestone
from .models import Transaction, EscrowAccount, FreelancerWallet, WithdrawalRequest
from .services import PaymentService


class WalletView(LoginRequiredMixin, FreelancerRequiredMixin, TemplateView):
    """View for freelancer wallet."""
    template_name = 'payments/wallet.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet, _ = FreelancerWallet.objects.get_or_create(user=self.request.user)
        context['wallet'] = wallet
        context['recent_transactions'] = Transaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:10]
        context['pending_withdrawals'] = WithdrawalRequest.objects.filter(
            wallet=wallet,
            status__in=['pending', 'processing']
        )
        return context


class TransactionHistoryView(LoginRequiredMixin, ListView):
    """View for transaction history."""
    model = Transaction
    template_name = 'payments/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class FundEscrowView(LoginRequiredMixin, ClientRequiredMixin, View):
    """View for funding escrow."""
    
    def get(self, request, contract_pk):
        contract = get_object_or_404(
            Contract, pk=contract_pk, client=request.user, status='active'
        )
        escrow, _ = EscrowAccount.objects.get_or_create(contract=contract)
        
        return render(request, 'payments/fund_escrow.html', {
            'contract': contract,
            'escrow': escrow,
            'remaining': contract.total_amount - escrow.balance,
        })
    
    def post(self, request, contract_pk):
        contract = get_object_or_404(
            Contract, pk=contract_pk, client=request.user, status='active'
        )
        
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            messages.error(request, 'Invalid amount.')
            return redirect('payments:fund_escrow', contract_pk=contract.pk)
        
        service = PaymentService()
        try:
            result = service.fund_escrow(contract, amount, request.user)
            messages.success(
                request, 
                f'Escrow funded with ${amount:.2f}. Reference: {result["reference"]}'
            )
        except Exception as e:
            messages.error(request, f'Payment failed: {str(e)}')
        
        return redirect('contracts:workspace', pk=contract.pk)


class ReleaseMilestonePaymentView(LoginRequiredMixin, ClientRequiredMixin, View):
    """View for releasing milestone payment."""
    
    def post(self, request, milestone_pk):
        milestone = get_object_or_404(
            Milestone,
            pk=milestone_pk,
            contract__client=request.user,
            status='approved'
        )
        
        service = PaymentService()
        try:
            result = service.release_milestone_payment(milestone, request.user)
            messages.success(
                request,
                f'Payment of ${result["net_amount"]:.2f} released to freelancer. '
                f'Platform fee: ${result["fee"]:.2f}'
            )
        except Exception as e:
            messages.error(request, f'Payment release failed: {str(e)}')
        
        return redirect('contracts:workspace', pk=milestone.contract.pk)


class RequestWithdrawalView(LoginRequiredMixin, FreelancerRequiredMixin, View):
    """View for requesting withdrawal."""
    
    def get(self, request):
        wallet, _ = FreelancerWallet.objects.get_or_create(user=request.user)
        return render(request, 'payments/withdrawal.html', {
            'wallet': wallet
        })
    
    def post(self, request):
        wallet, _ = FreelancerWallet.objects.get_or_create(user=request.user)
        
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            messages.error(request, 'Invalid amount.')
            return redirect('payments:withdrawal')
        
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero.')
            return redirect('payments:withdrawal')
        
        if amount > float(wallet.balance):
            messages.error(request, 'Insufficient balance.')
            return redirect('payments:withdrawal')
        
        WithdrawalRequest.objects.create(
            wallet=wallet,
            amount=amount,
            bank_name=request.POST.get('bank_name', 'Simulated Bank'),
            account_last_four=request.POST.get('account_last_four', '1234')
        )
        
        messages.success(
            request,
            f'Withdrawal request for ${amount:.2f} submitted. '
            'It will be processed within 24-48 hours.'
        )
        
        return redirect('payments:wallet')


class PaymentCheckoutView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    """Simulated payment checkout page."""
    template_name = 'payments/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract_pk = self.kwargs.get('contract_pk')
        context['contract'] = get_object_or_404(
            Contract, pk=contract_pk, client=self.request.user
        )
        return context
