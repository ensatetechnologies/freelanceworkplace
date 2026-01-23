"""
URL patterns for proposals app (web views).
"""
from django.urls import path
from . import views

app_name = 'proposals'

urlpatterns = [
    path('submit/<slug:project_slug>/', views.ProposalCreateView.as_view(), name='create'),
    path('my-proposals/', views.MyProposalsView.as_view(), name='my_proposals'),
    path('project/<slug:project_slug>/', views.ProjectProposalsView.as_view(), name='project_proposals'),
    path('<uuid:pk>/', views.ProposalDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.ProposalUpdateView.as_view(), name='edit'),
    path('<uuid:pk>/withdraw/', views.ProposalWithdrawView.as_view(), name='withdraw'),
    path('<uuid:pk>/accept/', views.ProposalAcceptView.as_view(), name='accept'),
    path('<uuid:pk>/reject/', views.ProposalRejectView.as_view(), name='reject'),
    path('<uuid:pk>/shortlist/', views.ProposalShortlistView.as_view(), name='shortlist'),
]
