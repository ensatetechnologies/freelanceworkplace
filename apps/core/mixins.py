"""
View mixins for the application.

Note: These mixins only inherit from UserPassesTestMixin, not LoginRequiredMixin.
When using these mixins in views, always include LoginRequiredMixin separately:
    class MyView(LoginRequiredMixin, ClientRequiredMixin, View):
        ...
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class FreelancerRequiredMixin(UserPassesTestMixin):
    """Mixin requiring freelancer role. Use with LoginRequiredMixin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'freelancer'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'This page is only accessible to freelancers.')
        return redirect('core:home')


class ClientRequiredMixin(UserPassesTestMixin):
    """Mixin requiring client role. Use with LoginRequiredMixin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'client'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'This page is only accessible to clients.')
        return redirect('core:home')


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin requiring admin role. Use with LoginRequiredMixin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_superuser
        )
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'This page is only accessible to administrators.')
        return redirect('core:home')


class ProfileCompleteMixin(UserPassesTestMixin):
    """Mixin requiring completed profile. Use with LoginRequiredMixin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_profile_complete
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.warning(self.request, 'Please complete your profile to access this page.')
        return redirect('accounts:profile_setup')


class VerifiedUserMixin(UserPassesTestMixin):
    """Mixin requiring verified user. Use with LoginRequiredMixin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_verified
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.warning(self.request, 'Please verify your email to access this page.')
        return redirect('accounts:verify_email')
