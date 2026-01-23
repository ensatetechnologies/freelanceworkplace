"""
Views for reviews app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from apps.contracts.models import Contract
from apps.accounts.models import User
from .models import Review
from .forms import ClientReviewForm, FreelancerReviewForm


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """View for creating reviews."""
    model = Review
    template_name = 'reviews/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.contract = get_object_or_404(
            Contract, pk=kwargs['contract_pk'], status='completed'
        )
        
        # Check if user is part of this contract
        if request.user not in [self.contract.client, self.contract.freelancer]:
            messages.error(request, 'You are not authorized to review this contract.')
            return redirect('core:dashboard')
        
        # Check if already reviewed
        if Review.objects.filter(contract=self.contract, reviewer=request.user).exists():
            messages.warning(request, 'You have already submitted a review for this contract.')
            return redirect('contracts:detail', pk=self.contract.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        if self.request.user == self.contract.client:
            return ClientReviewForm
        return FreelancerReviewForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract'] = self.contract
        if self.request.user == self.contract.client:
            context['reviewee'] = self.contract.freelancer
        else:
            context['reviewee'] = self.contract.client
        return context
    
    def form_valid(self, form):
        form.instance.contract = self.contract
        form.instance.reviewer = self.request.user
        messages.success(self.request, 'Thank you for your review!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('contracts:detail', kwargs={'pk': self.contract.pk})


class UserReviewsView(ListView):
    """View for listing user's reviews."""
    model = Review
    template_name = 'reviews/user_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        self.profile_user = get_object_or_404(User, pk=self.kwargs['user_pk'])
        return Review.objects.filter(
            reviewee=self.profile_user,
            is_visible=True
        ).select_related('reviewer', 'contract')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context


class ContractReviewsView(LoginRequiredMixin, ListView):
    """View for listing reviews for a contract."""
    model = Review
    template_name = 'reviews/contract_reviews.html'
    context_object_name = 'reviews'
    
    def get_queryset(self):
        self.contract = get_object_or_404(Contract, pk=self.kwargs['contract_pk'])
        return Review.objects.filter(contract=self.contract).select_related('reviewer', 'reviewee')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract'] = self.contract
        return context
