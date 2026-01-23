"""
API views for projects app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.db.models import Q

from apps.core.permissions import IsClient, IsProjectOwner
from .models import Project, Category, SavedProject
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    CategorySerializer
)


class ProjectListCreateView(generics.ListCreateAPIView):
    """List and create projects."""
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsClient()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectListSerializer
    
    def get_queryset(self):
        queryset = Project.objects.filter(status='open').select_related(
            'client', 'category'
        )
        
        # Search
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )
        
        # Category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Budget type filter
        budget_type = self.request.query_params.get('budget_type')
        if budget_type:
            queryset = queryset.filter(budget_type=budget_type)
        
        return queryset.order_by('-created_at')


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete project."""
    queryset = Project.objects.select_related('client', 'category')
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsProjectOwner()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectCreateSerializer
        return ProjectDetailSerializer


class ProjectPublishView(APIView):
    """Publish a project."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        project = Project.objects.filter(
            slug=slug, client=request.user, status='draft'
        ).first()
        
        if not project:
            return Response(
                {'error': 'Project not found or cannot be published.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        project.publish()
        return Response({'message': 'Project published successfully.'})


class MyProjectsView(generics.ListAPIView):
    """List current user's projects."""
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = ProjectListSerializer
    
    def get_queryset(self):
        return Project.objects.filter(
            client=self.request.user
        ).select_related('category').order_by('-created_at')


class CategoryListView(generics.ListAPIView):
    """List categories."""
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)


class SaveProjectView(APIView):
    """Save/unsave a project."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        project = Project.objects.filter(slug=slug).first()
        if not project:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        saved, created = SavedProject.objects.get_or_create(
            user=request.user, project=project
        )
        
        if not created:
            saved.delete()
            return Response({'saved': False, 'message': 'Project unsaved.'})
        
        return Response({'saved': True, 'message': 'Project saved.'})
