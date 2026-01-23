"""
URL patterns for payments app (web views).
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='transactions'),
    path('fund-escrow/<uuid:contract_pk>/', views.FundEscrowView.as_view(), name='fund_escrow'),
    path('release/<uuid:milestone_pk>/', views.ReleaseMilestonePaymentView.as_view(), name='release_payment'),
    path('withdrawal/', views.RequestWithdrawalView.as_view(), name='withdrawal'),
    path('checkout/<uuid:contract_pk>/', views.PaymentCheckoutView.as_view(), name='checkout'),
]
