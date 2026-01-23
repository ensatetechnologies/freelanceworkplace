"""
API URL patterns for payments app.
"""
from django.urls import path
from . import api_views

app_name = 'payments_api'

urlpatterns = [
    path('transactions/', api_views.TransactionListView.as_view(), name='transactions'),
    path('wallet/', api_views.WalletView.as_view(), name='wallet'),
    path('fund-escrow/<uuid:contract_pk>/', api_views.FundEscrowView.as_view(), name='fund_escrow'),
    path('release/<uuid:milestone_pk>/', api_views.ReleaseMilestonePaymentView.as_view(), name='release'),
    path('withdrawals/', api_views.WithdrawalListCreateView.as_view(), name='withdrawals'),
]
