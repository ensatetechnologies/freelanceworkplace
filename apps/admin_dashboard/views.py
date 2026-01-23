"""
Views for admin dashboard app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from apps.core.mixins import AdminRequiredMixin
from apps.accounts.models import User, FreelancerProfile, ClientProfile
from apps.projects.models import Project, Category
from apps.contracts.models import Contract
from apps.payments.models import Transaction, WithdrawalRequest
from apps.payments.services import PaymentService


class DashboardHomeView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin dashboard home with statistics."""
    template_name = 'admin_dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User stats
        context['total_users'] = User.objects.count()
        context['total_freelancers'] = User.objects.filter(role='freelancer').count()
        context['total_clients'] = User.objects.filter(role='client').count()
        context['new_users_week'] = User.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Project stats
        context['total_projects'] = Project.objects.count()
        context['open_projects'] = Project.objects.filter(status='open').count()
        context['active_contracts'] = Contract.objects.filter(status='active').count()
        context['completed_contracts'] = Contract.objects.filter(status='completed').count()
        
        # Financial stats
        context['total_transactions'] = Transaction.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context['platform_fees'] = Transaction.objects.filter(
            type='platform_fee', status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context['pending_withdrawals'] = WithdrawalRequest.objects.filter(
            status__in=['pending', 'approved']
        ).count()
        
        # Recent activity
        context['recent_projects'] = Project.objects.order_by('-created_at')[:5]
        context['recent_users'] = User.objects.order_by('-created_at')[:5]
        
        return context


class UserManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin view for managing users."""
    model = User
    template_name = 'admin_dashboard/users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        search = self.request.GET.get('q')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(email__icontains=search) | 
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset


class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Admin view for user details."""
    model = User
    template_name = 'admin_dashboard/user_detail.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        if user.role == 'freelancer':
            context['profile'] = getattr(user, 'freelancer_profile', None)
            context['contracts'] = user.freelancer_contracts.all()[:10]
        else:
            context['profile'] = getattr(user, 'client_profile', None)
            context['projects'] = user.projects.all()[:10]
            context['contracts'] = user.client_contracts.all()[:10]
        
        context['transactions'] = Transaction.objects.filter(user=user)[:10]
        
        return context


class ProjectManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin view for managing projects."""
    model = Project
    template_name = 'admin_dashboard/projects.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Project.objects.select_related('client', 'category').order_by('-created_at')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


class ContractManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin view for managing contracts."""
    model = Contract
    template_name = 'admin_dashboard/contracts.html'
    context_object_name = 'contracts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Contract.objects.select_related(
            'client', 'freelancer', 'project'
        ).order_by('-created_at')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


class WithdrawalManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin view for managing withdrawal requests."""
    model = WithdrawalRequest
    template_name = 'admin_dashboard/withdrawals.html'
    context_object_name = 'withdrawals'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = WithdrawalRequest.objects.select_related(
            'wallet__user'
        ).order_by('-created_at')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


class ProcessWithdrawalView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Admin view for processing withdrawals."""
    
    def post(self, request, pk):
        withdrawal = get_object_or_404(WithdrawalRequest, pk=pk)
        action = request.POST.get('action')
        
        if action == 'approve':
            withdrawal.approve()
            messages.success(request, 'Withdrawal approved.')
        elif action == 'process':
            service = PaymentService()
            try:
                service.process_withdrawal(withdrawal)
                messages.success(request, 'Withdrawal processed successfully.')
            except Exception as e:
                messages.error(request, f'Processing failed: {str(e)}')
        elif action == 'reject':
            notes = request.POST.get('notes', '')
            withdrawal.reject(notes)
            messages.success(request, 'Withdrawal rejected.')
        
        return redirect('admin_dashboard:withdrawals')


class CategoryManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin view for managing categories."""
    model = Category
    template_name = 'admin_dashboard/categories.html'
    context_object_name = 'categories'


class ReportsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin reports view."""
    template_name = 'admin_dashboard/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date range
        days = int(self.request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Transaction summary
        context['transaction_summary'] = Transaction.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).values('type').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        # Projects by category
        context['projects_by_category'] = Project.objects.filter(
            created_at__gte=start_date
        ).values('category__name').annotate(count=Count('id'))
        
        # User growth
        context['user_growth'] = User.objects.filter(
            created_at__gte=start_date
        ).values('role').annotate(count=Count('id'))
        
        context['days'] = days
        
        return context
