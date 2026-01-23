"""
API URL patterns for projects app.
"""
from django.urls import path
from . import api_views

app_name = 'projects_api'

urlpatterns = [
    path('', api_views.ProjectListCreateView.as_view(), name='list_create'),
    path('my-projects/', api_views.MyProjectsView.as_view(), name='my_projects'),
    path('categories/', api_views.CategoryListView.as_view(), name='categories'),
    path('<slug:slug>/', api_views.ProjectDetailView.as_view(), name='detail'),
    path('<slug:slug>/publish/', api_views.ProjectPublishView.as_view(), name='publish'),
    path('<slug:slug>/save/', api_views.SaveProjectView.as_view(), name='save'),
]
