"""
Views for accounts app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView, DetailView, UpdateView, ListView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Avg

from .models import User, FreelancerProfile, ClientProfile
from .forms import UserUpdateForm, FreelancerProfileForm, ClientProfileForm


class ProfileSetupView(LoginRequiredMixin, TemplateView):
    """View for initial profile setup after registration."""
    template_name = 'accounts/profile_setup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user_form'] = UserUpdateForm(instance=user)
        
        if user.role == 'freelancer':
            profile, _ = FreelancerProfile.objects.get_or_create(user=user)
            context['profile_form'] = FreelancerProfileForm(instance=profile)
        else:
            profile, _ = ClientProfile.objects.get_or_create(user=user)
            context['profile_form'] = ClientProfileForm(instance=profile)
        
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        
        if user.role == 'freelancer':
            profile = user.freelancer_profile
            profile_form = FreelancerProfileForm(request.POST, instance=profile)
        else:
            profile = user.client_profile
            profile_form = ClientProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            user.is_profile_complete = True
            user.save()
            messages.success(request, 'Your profile has been set up successfully!')
            return redirect('core:dashboard')
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })


class ProfileView(DetailView):
    """View for displaying user profile."""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        if user.role == 'freelancer':
            context['profile'] = getattr(user, 'freelancer_profile', None)
            context['reviews'] = user.reviews_received.filter(
                is_visible=True
            ).select_related('reviewer')[:5]
            context['completed_contracts'] = user.freelancer_contracts.filter(
                status='completed'
            ).select_related('project')[:5]
        else:
            context['profile'] = getattr(user, 'client_profile', None)
            context['reviews'] = user.reviews_received.filter(
                is_visible=True
            ).select_related('reviewer')[:5]
            context['posted_projects'] = user.projects.filter(
                status__in=['open', 'completed']
            )[:5]
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """View for editing own profile."""
    template_name = 'accounts/profile_edit.html'
    
    def get_object(self):
        return self.request.user
    
    def get_form_class(self):
        return UserUpdateForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'freelancer':
            profile = user.freelancer_profile
            context['profile_form'] = FreelancerProfileForm(instance=profile)
        else:
            profile = user.client_profile
            context['profile_form'] = ClientProfileForm(instance=profile)
        
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        
        if user.role == 'freelancer':
            profile = user.freelancer_profile
            profile_form = FreelancerProfileForm(request.POST, instance=profile)
        else:
            profile = user.client_profile
            profile_form = ClientProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile', pk=user.pk)
        
        return render(request, self.template_name, {
            'form': user_form,
            'profile_form': profile_form,
        })
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'pk': self.request.user.pk})


class FreelancerListView(ListView):
    """View for listing freelancers."""
    model = FreelancerProfile
    template_name = 'accounts/freelancer_list.html'
    context_object_name = 'freelancers'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = FreelancerProfile.objects.select_related('user').filter(
            user__is_profile_complete=True
        )
        
        # Filter by skill
        skill = self.request.GET.get('skill')
        if skill:
            queryset = queryset.filter(skills__contains=skill)
        
        # Filter by availability
        availability = self.request.GET.get('availability')
        if availability:
            queryset = queryset.filter(availability=availability)
        
        # Filter by hourly rate range
        min_rate = self.request.GET.get('min_rate')
        max_rate = self.request.GET.get('max_rate')
        if min_rate:
            queryset = queryset.filter(hourly_rate__gte=min_rate)
        if max_rate:
            queryset = queryset.filter(hourly_rate__lte=max_rate)
        
        # Ordering
        order = self.request.GET.get('order', '-avg_rating')
        queryset = queryset.order_by(order)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'skill': self.request.GET.get('skill', ''),
            'availability': self.request.GET.get('availability', ''),
            'min_rate': self.request.GET.get('min_rate', ''),
            'max_rate': self.request.GET.get('max_rate', ''),
            'order': self.request.GET.get('order', '-avg_rating'),
        }
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    """Account settings view."""
    template_name = 'accounts/settings.html'
