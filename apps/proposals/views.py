"""
Views for proposals app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.db import models

from apps.core.mixins import FreelancerRequiredMixin, ClientRequiredMixin
from apps.projects.models import Project
from .models import Proposal
from .forms import ProposalForm


class ProposalCreateView(LoginRequiredMixin, FreelancerRequiredMixin, CreateView):
    """View for creating proposals."""
    model = Proposal
    form_class = ProposalForm
    template_name = 'proposals/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=kwargs['project_slug'], status='open')
        
        # Check if already submitted a proposal
        if Proposal.objects.filter(project=self.project, freelancer=request.user).exists():
            messages.warning(request, 'You have already submitted a proposal for this project.')
            return redirect('projects:detail', slug=self.project.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.project
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
    
    def form_valid(self, form):
        form.instance.project = self.project
        form.instance.freelancer = self.request.user
        
        # Update project proposals count
        self.project.proposals_count += 1
        self.project.save(update_fields=['proposals_count'])
        
        messages.success(self.request, 'Proposal submitted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('proposals:my_proposals')


class ProposalDetailView(LoginRequiredMixin, DetailView):
    """View for proposal detail."""
    model = Proposal
    template_name = 'proposals/detail.html'
    context_object_name = 'proposal'
    
    def get_queryset(self):
        user = self.request.user
        # Allow access to proposal owner (freelancer) or project owner (client)
        return Proposal.objects.filter(
            models.Q(freelancer=user) | models.Q(project__client=user)
        ).select_related('project', 'freelancer', 'project__client')
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Mark as viewed if client is viewing
        if request.user == self.object.project.client:
            self.object.mark_viewed()
        
        return response


class ProposalUpdateView(LoginRequiredMixin, FreelancerRequiredMixin, UpdateView):
    """View for updating proposals."""
    model = Proposal
    form_class = ProposalForm
    template_name = 'proposals/edit.html'
    
    def get_queryset(self):
        return Proposal.objects.filter(
            freelancer=self.request.user,
            status='pending'
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.object.project
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Proposal updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('proposals:detail', kwargs={'pk': self.object.pk})


class ProposalWithdrawView(LoginRequiredMixin, FreelancerRequiredMixin, View):
    """View for withdrawing a proposal."""
    
    def post(self, request, pk):
        proposal = get_object_or_404(
            Proposal,
            pk=pk,
            freelancer=request.user,
            status__in=['pending', 'shortlisted']
        )
        proposal.withdraw()
        messages.success(request, 'Proposal withdrawn successfully.')
        return redirect('proposals:my_proposals')


class MyProposalsView(LoginRequiredMixin, FreelancerRequiredMixin, ListView):
    """View for listing freelancer's proposals."""
    model = Proposal
    template_name = 'proposals/my_proposals.html'
    context_object_name = 'proposals'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Proposal.objects.filter(
            freelancer=self.request.user
        ).select_related('project', 'project__client')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['total_count'] = user.proposals.count()
        context['pending_count'] = user.proposals.filter(status='pending').count()
        context['shortlisted_count'] = user.proposals.filter(status='shortlisted').count()
        context['accepted_count'] = user.proposals.filter(status='accepted').count()
        context['rejected_count'] = user.proposals.filter(status='rejected').count()
        return context


class ProjectProposalsView(LoginRequiredMixin, ClientRequiredMixin, ListView):
    """View for listing proposals for a specific project."""
    model = Proposal
    template_name = 'proposals/project_proposals.html'
    context_object_name = 'proposals'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(
            Project, slug=kwargs['project_slug'], client=request.user
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Proposal.objects.filter(
            project=self.project
        ).select_related('freelancer').prefetch_related('attachments')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['pending_count'] = self.project.proposals.filter(status='pending').count()
        context['shortlisted_count'] = self.project.proposals.filter(status='shortlisted').count()
        return context


class ProposalAcceptView(LoginRequiredMixin, ClientRequiredMixin, View):
    """View for accepting a proposal."""
    
    def post(self, request, pk):
        proposal = get_object_or_404(
            Proposal,
            pk=pk,
            project__client=request.user,
            status__in=['pending', 'shortlisted']
        )
        proposal.accept()
        
        # Create contract
        from apps.contracts.models import Contract
        Contract.objects.create(
            project=proposal.project,
            proposal=proposal,
            client=proposal.project.client,
            freelancer=proposal.freelancer,
            title=proposal.project.title,
            description=proposal.project.description,
            total_amount=proposal.bid_amount,
            start_date=timezone.now().date()
        )
        
        messages.success(request, 'Proposal accepted! A contract has been created.')
        return redirect('contracts:detail', pk=proposal.contract.pk)


class ProposalRejectView(LoginRequiredMixin, ClientRequiredMixin, View):
    """View for rejecting a proposal."""
    
    def post(self, request, pk):
        proposal = get_object_or_404(
            Proposal,
            pk=pk,
            project__client=request.user,
            status__in=['pending', 'shortlisted']
        )
        proposal.reject()
        messages.success(request, 'Proposal rejected.')
        return redirect('proposals:project_proposals', project_slug=proposal.project.slug)


class ProposalShortlistView(LoginRequiredMixin, ClientRequiredMixin, View):
    """View for shortlisting a proposal."""
    
    def post(self, request, pk):
        proposal = get_object_or_404(
            Proposal,
            pk=pk,
            project__client=request.user,
            status='pending'
        )
        proposal.shortlist()
        messages.success(request, 'Proposal shortlisted.')
        return redirect('proposals:project_proposals', project_slug=proposal.project.slug)
