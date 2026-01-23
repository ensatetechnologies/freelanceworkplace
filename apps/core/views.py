"""
Core views for the application.
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.projects.models import Project, Category


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_projects'] = Project.objects.filter(
            status='open', is_featured=True
        ).select_related('client', 'category')[:6]
        context['recent_projects'] = Project.objects.filter(
            status='open'
        ).select_related('client', 'category')[:8]
        context['categories'] = Category.objects.filter(is_active=True)[:8]
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard view."""
    template_name = 'core/dashboard.html'
    
    def get_template_names(self):
        if self.request.user.role == 'freelancer':
            return ['core/dashboard_freelancer.html']
        elif self.request.user.role == 'client':
            return ['core/dashboard_client.html']
        return ['core/dashboard.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'freelancer':
            context['active_contracts'] = user.freelancer_contracts.filter(
                status='active'
            ).select_related('project', 'client')[:5]
            context['pending_proposals'] = user.proposals.filter(
                status='pending'
            ).select_related('project')[:5]
            context['recent_projects'] = Project.objects.filter(
                status='open'
            ).select_related('client', 'category')[:5]
        elif user.role == 'client':
            context['my_projects'] = user.projects.all()[:5]
            context['active_contracts'] = user.client_contracts.filter(
                status='active'
            ).select_related('project', 'freelancer')[:5]
            context['pending_proposals'] = user.projects.filter(
                status='open'
            ).values_list('proposals', flat=True)[:5]
        
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """Contact page view."""
    template_name = 'core/contact.html'


class HowItWorksView(TemplateView):
    """How it works page view."""
    template_name = 'core/how_it_works.html'
