"""
URL patterns for contracts app (web views).
"""
from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.ContractListView.as_view(), name='list'),
    path('<uuid:pk>/', views.ContractDetailView.as_view(), name='detail'),
    path('<uuid:pk>/workspace/', views.ContractWorkspaceView.as_view(), name='workspace'),
    path('<uuid:pk>/complete/', views.ContractCompleteView.as_view(), name='complete'),
    path('<uuid:contract_pk>/milestones/add/', views.MilestoneCreateView.as_view(), name='milestone_add'),
    path('milestones/<uuid:pk>/start/', views.MilestoneStartView.as_view(), name='milestone_start'),
    path('milestones/<uuid:pk>/submit/', views.MilestoneSubmitView.as_view(), name='milestone_submit'),
    path('milestones/<uuid:pk>/approve/', views.MilestoneApproveView.as_view(), name='milestone_approve'),
    path('milestones/<uuid:pk>/revision/', views.MilestoneRevisionView.as_view(), name='milestone_revision'),
    path('milestones/<uuid:milestone_pk>/deliverable/upload/', views.DeliverableUploadView.as_view(), name='deliverable_upload'),
]
