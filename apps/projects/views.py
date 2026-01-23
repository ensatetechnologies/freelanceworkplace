"""
Views for projects app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.views import View

from apps.core.mixins import ClientRequiredMixin, ProfileCompleteMixin
from .models import Project, Category, ProjectAttachment, SavedProject
from .forms import ProjectForm, ProjectSearchForm, ProjectAttachmentForm


class ProjectListView(ListView):
    """View for listing projects."""
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Project.objects.filter(status='open').select_related(
            'client', 'category'
        )
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Budget type filter
        budget_type = self.request.GET.get('budget_type')
        if budget_type:
            queryset = queryset.filter(budget_type=budget_type)
        
        # Experience level filter
        experience_level = self.request.GET.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        # Budget range filter
        min_budget = self.request.GET.get('min_budget')
        max_budget = self.request.GET.get('max_budget')
        if min_budget:
            queryset = queryset.filter(budget_max__gte=min_budget)
        if max_budget:
            queryset = queryset.filter(budget_min__lte=max_budget)
        
        # Ordering
        order = self.request.GET.get('order', '-created_at')
        if order == 'budget_high':
            queryset = queryset.order_by('-budget_max')
        elif order == 'budget_low':
            queryset = queryset.order_by('budget_min')
        elif order == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['search_form'] = ProjectSearchForm(self.request.GET)
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'category': self.request.GET.get('category', ''),
            'budget_type': self.request.GET.get('budget_type', ''),
            'experience_level': self.request.GET.get('experience_level', ''),
            'order': self.request.GET.get('order', '-created_at'),
        }
        return context


class ProjectDetailView(DetailView):
    """View for project detail."""
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Project.objects.select_related('client', 'category').prefetch_related(
            'attachments', 'proposals'
        )
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Increment view count
        self.object.increment_views()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Check if user has already submitted a proposal
        if user.is_authenticated and user.role == 'freelancer':
            context['has_proposal'] = self.object.proposals.filter(
                freelancer=user
            ).exists()
            context['is_saved'] = SavedProject.objects.filter(
                user=user, project=self.object
            ).exists()
        
        # Get similar projects
        context['similar_projects'] = Project.objects.filter(
            category=self.object.category,
            status='open'
        ).exclude(pk=self.object.pk)[:4]
        
        return context


class ProjectCreateView(LoginRequiredMixin, ClientRequiredMixin, CreateView):
    """View for creating projects."""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create.html'
    
    def form_valid(self, form):
        form.instance.client = self.request.user
        messages.success(self.request, 'Project created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'slug': self.object.slug})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating projects."""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/edit.html'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Project.objects.filter(client=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'slug': self.object.slug})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting projects."""
    model = Project
    template_name = 'projects/delete_confirm.html'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('projects:my_projects')
    
    def get_queryset(self):
        return Project.objects.filter(client=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ProjectPublishView(LoginRequiredMixin, View):
    """View for publishing a project."""
    
    def post(self, request, slug):
        project = get_object_or_404(
            Project, slug=slug, client=request.user, status='draft'
        )
        project.publish()
        messages.success(request, 'Project published successfully!')
        return redirect('projects:detail', slug=project.slug)


class MyProjectsView(LoginRequiredMixin, ClientRequiredMixin, ListView):
    """View for listing user's projects."""
    model = Project
    template_name = 'projects/my_projects.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        return Project.objects.filter(
            client=self.request.user
        ).select_related('category').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['draft_count'] = user.projects.filter(status='draft').count()
        context['open_count'] = user.projects.filter(status='open').count()
        context['in_progress_count'] = user.projects.filter(status='in_progress').count()
        context['completed_count'] = user.projects.filter(status='completed').count()
        return context


class SaveProjectView(LoginRequiredMixin, View):
    """View for saving/unsaving a project."""
    
    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        saved, created = SavedProject.objects.get_or_create(
            user=request.user, project=project
        )
        
        if not created:
            saved.delete()
            return JsonResponse({'saved': False})
        
        return JsonResponse({'saved': True})


class SavedProjectsView(LoginRequiredMixin, ListView):
    """View for listing saved projects."""
    model = SavedProject
    template_name = 'projects/saved.html'
    context_object_name = 'saved_projects'
    paginate_by = 12
    
    def get_queryset(self):
        return SavedProject.objects.filter(
            user=self.request.user
        ).select_related('project', 'project__client', 'project__category')


class CategoryListView(ListView):
    """View for listing categories."""
    model = Category
    template_name = 'projects/categories.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
