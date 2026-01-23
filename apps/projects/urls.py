"""
URL patterns for projects app (web views).
"""
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('my-projects/', views.MyProjectsView.as_view(), name='my_projects'),
    path('saved/', views.SavedProjectsView.as_view(), name='saved'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('<slug:slug>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
    path('<slug:slug>/publish/', views.ProjectPublishView.as_view(), name='publish'),
    path('<slug:slug>/save/', views.SaveProjectView.as_view(), name='save'),
]
