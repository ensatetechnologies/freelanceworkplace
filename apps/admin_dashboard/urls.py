"""
URL patterns for admin dashboard app.
"""
from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('users/', views.UserManagementView.as_view(), name='users'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('projects/', views.ProjectManagementView.as_view(), name='projects'),
    path('contracts/', views.ContractManagementView.as_view(), name='contracts'),
    path('withdrawals/', views.WithdrawalManagementView.as_view(), name='withdrawals'),
    path('withdrawals/<uuid:pk>/process/', views.ProcessWithdrawalView.as_view(), name='process_withdrawal'),
    path('categories/', views.CategoryManagementView.as_view(), name='categories'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
]
