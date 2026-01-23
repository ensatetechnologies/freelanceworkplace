"""
Views for contracts app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse

from .models import Contract, Milestone, Deliverable, ContractActivity
from .forms import MilestoneForm, DeliverableForm, RevisionRequestForm


class ContractListView(LoginRequiredMixin, ListView):
    """View for listing user's contracts."""
    model = Contract
    template_name = 'contracts/list.html'
    context_object_name = 'contracts'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        queryset = Contract.objects.filter(
            Q(client=user) | Q(freelancer=user)
        ).select_related('project', 'client', 'freelancer')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'client':
            contracts = user.client_contracts
        else:
            contracts = user.freelancer_contracts
        
        context['active_count'] = contracts.filter(status='active').count()
        context['completed_count'] = contracts.filter(status='completed').count()
        return context


class ContractDetailView(LoginRequiredMixin, DetailView):
    """View for contract detail."""
    model = Contract
    template_name = 'contracts/detail.html'
    context_object_name = 'contract'
    
    def get_queryset(self):
        user = self.request.user
        return Contract.objects.filter(
            Q(client=user) | Q(freelancer=user)
        ).select_related('project', 'client', 'freelancer', 'proposal')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['milestones'] = self.object.milestones.prefetch_related('deliverables')
        context['activities'] = self.object.activities.select_related('user')[:10]
        context['is_client'] = self.request.user == self.object.client
        context['is_freelancer'] = self.request.user == self.object.freelancer
        return context


class ContractWorkspaceView(LoginRequiredMixin, DetailView):
    """Contract workspace view for managing milestones."""
    model = Contract
    template_name = 'contracts/workspace.html'
    context_object_name = 'contract'
    
    def get_queryset(self):
        user = self.request.user
        return Contract.objects.filter(
            Q(client=user) | Q(freelancer=user)
        ).select_related('project', 'client', 'freelancer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['milestones'] = self.object.milestones.prefetch_related('deliverables')
        context['milestone_form'] = MilestoneForm()
        context['deliverable_form'] = DeliverableForm()
        context['revision_form'] = RevisionRequestForm()
        context['is_client'] = self.request.user == self.object.client
        context['is_freelancer'] = self.request.user == self.object.freelancer
        return context


class MilestoneCreateView(LoginRequiredMixin, View):
    """View for creating milestones."""
    
    def post(self, request, contract_pk):
        contract = get_object_or_404(
            Contract, pk=contract_pk, client=request.user, status='active'
        )
        
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.contract = contract
            milestone.order = contract.milestones.count()
            milestone.save()
            
            # Log activity
            ContractActivity.objects.create(
                contract=contract,
                user=request.user,
                activity_type=ContractActivity.ActivityType.MILESTONE_ADDED,
                description=f'Added milestone: {milestone.title}'
            )
            
            messages.success(request, 'Milestone added successfully!')
        else:
            messages.error(request, 'Error adding milestone. Please check the form.')
        
        return redirect('contracts:workspace', pk=contract.pk)


class MilestoneStartView(LoginRequiredMixin, View):
    """View for starting a milestone."""
    
    def post(self, request, pk):
        milestone = get_object_or_404(
            Milestone,
            pk=pk,
            contract__freelancer=request.user,
            status='pending'
        )
        milestone.start()
        
        # Log activity
        ContractActivity.objects.create(
            contract=milestone.contract,
            user=request.user,
            activity_type=ContractActivity.ActivityType.MILESTONE_STARTED,
            description=f'Started working on: {milestone.title}'
        )
        
        messages.success(request, 'Milestone started!')
        return redirect('contracts:workspace', pk=milestone.contract.pk)


class MilestoneSubmitView(LoginRequiredMixin, View):
    """View for submitting a milestone."""
    
    def post(self, request, pk):
        milestone = get_object_or_404(
            Milestone,
            pk=pk,
            contract__freelancer=request.user,
            status__in=['in_progress', 'revision']
        )
        milestone.submit()
        
        # Log activity
        ContractActivity.objects.create(
            contract=milestone.contract,
            user=request.user,
            activity_type=ContractActivity.ActivityType.MILESTONE_SUBMITTED,
            description=f'Submitted milestone: {milestone.title}'
        )
        
        messages.success(request, 'Milestone submitted for review!')
        return redirect('contracts:workspace', pk=milestone.contract.pk)


class MilestoneApproveView(LoginRequiredMixin, View):
    """View for approving a milestone."""
    
    def post(self, request, pk):
        milestone = get_object_or_404(
            Milestone,
            pk=pk,
            contract__client=request.user,
            status='submitted'
        )
        milestone.approve()
        
        # Log activity
        ContractActivity.objects.create(
            contract=milestone.contract,
            user=request.user,
            activity_type=ContractActivity.ActivityType.MILESTONE_APPROVED,
            description=f'Approved milestone: {milestone.title}'
        )
        
        messages.success(request, 'Milestone approved!')
        return redirect('contracts:workspace', pk=milestone.contract.pk)


class MilestoneRevisionView(LoginRequiredMixin, View):
    """View for requesting revision on a milestone."""
    
    def post(self, request, pk):
        milestone = get_object_or_404(
            Milestone,
            pk=pk,
            contract__client=request.user,
            status='submitted'
        )
        
        form = RevisionRequestForm(request.POST)
        if form.is_valid():
            milestone.request_revision(form.cleaned_data['notes'])
            
            # Log activity
            ContractActivity.objects.create(
                contract=milestone.contract,
                user=request.user,
                activity_type=ContractActivity.ActivityType.MILESTONE_REVISION,
                description=f'Requested revision on: {milestone.title}'
            )
            
            messages.success(request, 'Revision requested.')
        
        return redirect('contracts:workspace', pk=milestone.contract.pk)


class DeliverableUploadView(LoginRequiredMixin, View):
    """View for uploading deliverables."""
    
    def post(self, request, milestone_pk):
        milestone = get_object_or_404(
            Milestone,
            pk=milestone_pk,
            contract__freelancer=request.user,
            status__in=['in_progress', 'revision']
        )
        
        form = DeliverableForm(request.POST, request.FILES)
        if form.is_valid():
            deliverable = form.save(commit=False)
            deliverable.milestone = milestone
            deliverable.save()
            messages.success(request, 'Deliverable uploaded successfully!')
        else:
            messages.error(request, 'Error uploading deliverable.')
        
        return redirect('contracts:workspace', pk=milestone.contract.pk)


class ContractCompleteView(LoginRequiredMixin, View):
    """View for completing a contract."""
    
    def post(self, request, pk):
        contract = get_object_or_404(
            Contract,
            pk=pk,
            client=request.user,
            status='active'
        )
        
        # Check if all milestones are approved/paid
        pending = contract.milestones.exclude(status__in=['approved', 'paid']).exists()
        if pending:
            messages.error(request, 'Cannot complete contract. Some milestones are still pending.')
            return redirect('contracts:workspace', pk=contract.pk)
        
        contract.complete()
        
        # Log activity
        ContractActivity.objects.create(
            contract=contract,
            user=request.user,
            activity_type=ContractActivity.ActivityType.CONTRACT_COMPLETED,
            description='Contract completed successfully'
        )
        
        messages.success(request, 'Contract completed! You can now leave a review.')
        return redirect('reviews:create', contract_pk=contract.pk)
